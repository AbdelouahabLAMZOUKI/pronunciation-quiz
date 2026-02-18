import argparse
import json
import random
import webbrowser
from pathlib import Path
from typing import Any


def load_words(json_path: Path) -> list[dict]:
    """Load word entries from a JSON file."""
    with json_path.open("r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of word objects.")
    return data


def load_words_firestore(
    collection_name: str,
    project_id: str | None,
    service_account_path: str | None,
    limit: int | None,
    order_by: str | None,
    order_dir: str,
    start_after: str | None,
) -> list[dict]:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError as exc:
        raise RuntimeError("firebase-admin is not installed.") from exc

    try:
        if not firebase_admin._apps:
            if service_account_path:
                cred = credentials.Certificate(service_account_path)
            else:
                cred = credentials.ApplicationDefault()
            options: dict[str, Any] = {}
            if project_id:
                options["projectId"] = project_id
            firebase_admin.initialize_app(cred, options or None)
        db = firestore.client()
        collection = db.collection(collection_name)
        if order_by:
            direction = firestore.Query.ASCENDING if order_dir == "asc" else firestore.Query.DESCENDING
            collection = collection.order_by(order_by, direction=direction)
        if start_after:
            start_doc = collection.document(start_after).get()
            if start_doc.exists:
                collection = collection.start_after(start_doc)
        if limit and limit > 0:
            collection = collection.limit(limit)
        docs = collection.stream()
    except Exception as exc:
        raise RuntimeError("Failed to connect to Firestore.") from exc

    words: list[dict] = []
    for doc in docs:
        data = doc.to_dict()
        if isinstance(data, dict):
            words.append(data)
    return words


def resolve_clip_location(
    clip_id: str,
    base_dir: Path,
    clips_dir: str,
    template: str,
    clip_url: str | None,
) -> str:
    """Resolve a clip_id to a local path or URL placeholder."""
    if clip_url:
        return clip_url
    filename = template.format(clip_id=clip_id)
    return str((base_dir / clips_dir / filename).resolve())


def maybe_open_clip(clip_location: str, open_clip: bool) -> None:
    if not open_clip:
        return
    try:
        webbrowser.open(clip_location)
    except Exception:
        print("Unable to open clip location.")


def run_round(
    words: list[dict],
    base_dir: Path,
    clips_dir: str,
    clip_template: str,
    clip_url_field: str,
    open_clip: bool,
) -> tuple[int, int, bool, bool, str, str, bool]:
    word = random.choice(words)
    text = word.get("text", "<missing>")
    feature = word.get("feature_id", "<missing>")
    allowed_features = {"stress", "rhythm", "assimilation", "t_flap", "intonation"}
    if feature not in allowed_features:
        raise ValueError(f"Unexpected feature_id: {feature}")
    clip_id = word.get("clip_id", "<missing>")
    clip_url = word.get(clip_url_field)
    syllables = word.get("syllables", [])
    original_pronunciation = word.get("original_pronunciation", False)
    ipa_pronunciation = word.get("ipa_pronunciation", "")
    print(f"Random word: {text}")
    clip_location = resolve_clip_location(
        clip_id,
        base_dir,
        clips_dir,
        clip_template,
        clip_url,
    )
    print(f"Clip ID: {clip_id}")
    print(f"Clip location: {clip_location}")
    maybe_open_clip(clip_location, open_clip)
    attempts = 0
    wrong_guesses = 0
    skipped = False
    correct = False
    show_ipa = True
    show_syllables = True
    show_original_flag = True
    while True:
        if show_syllables and isinstance(syllables, list) and syllables:
            print("Syllables:")
            print(" | ".join(syllables))
        if show_ipa and ipa_pronunciation:
            print(f"IPA: {ipa_pronunciation}")
        if show_original_flag:
            print(f"Original pronunciation flag: {original_pronunciation}")
        guess = input(
            "Guess the feature (stress, rhythm, assimilation, t_flap, intonation) or 'skip'/'quit': "
        ).strip()
        normalized = guess.lower()
        if normalized in {"help", "?"}:
            print("Commands: ipa/noipa, syllables/nosyllables, original/nooriginal, skip, quit")
            continue
        if normalized in {"ipa", "showipa"}:
            show_ipa = True
            print("IPA display enabled.")
            continue
        if normalized in {"noipa", "hideipa"}:
            show_ipa = False
            print("IPA display hidden.")
            continue
        if normalized in {"syllables", "showsyllables"}:
            show_syllables = True
            print("Syllables display enabled.")
            continue
        if normalized in {"nosyllables", "hidesyllables"}:
            show_syllables = False
            print("Syllables display hidden.")
            continue
        if normalized in {"original", "showoriginal"}:
            show_original_flag = True
            print("Original flag display enabled.")
            continue
        if normalized in {"nooriginal", "hideoriginal"}:
            show_original_flag = False
            print("Original flag display hidden.")
            continue
        if normalized in {"quit", "q", "exit"}:
            return attempts, wrong_guesses, False, False, feature, text, True
        if normalized == "skip":
            attempts += 1
            print(f"Skipped. Correct feature: {feature}")
            skipped = True
            break
        if normalized not in allowed_features:
            print("Invalid feature. Try again.")
            continue
        attempts += 1
        if normalized == feature:
            print("Correct!")
            correct = True
            break
        print("Wrong! Try again.")
        wrong_guesses += 1

    print(f"Attempts: {attempts}")
    return attempts, wrong_guesses, skipped, correct, feature, text, False


def init_stats() -> dict:
    return {
        "total_rounds": 0,
        "total_attempts": 0,
        "correct": 0,
        "skipped": 0,
        "per_feature": {
            "stress": {"rounds": 0, "correct": 0},
            "rhythm": {"rounds": 0, "correct": 0},
            "assimilation": {"rounds": 0, "correct": 0},
            "t_flap": {"rounds": 0, "correct": 0},
            "intonation": {"rounds": 0, "correct": 0},
        },
        "missed_words": {},
        "attempts_per_word": {},
    }


def update_stats(
    stats: dict,
    attempts: int,
    wrong_guesses: int,
    skipped: bool,
    correct: bool,
    feature: str,
    text: str,
) -> None:
    stats["total_rounds"] += 1
    stats["total_attempts"] += attempts
    if skipped:
        stats["skipped"] += 1
        stats["missed_words"][text] = stats["missed_words"].get(text, 0) + 1
    if correct:
        stats["correct"] += 1
    stats["per_feature"][feature]["rounds"] += 1
    if correct:
        stats["per_feature"][feature]["correct"] += 1
    if wrong_guesses > 0:
        stats["missed_words"][text] = stats["missed_words"].get(text, 0) + wrong_guesses
    attempts_per_word = stats["attempts_per_word"].setdefault(text, {"rounds": 0, "attempts": 0})
    attempts_per_word["rounds"] += 1
    attempts_per_word["attempts"] += attempts


def print_stats(stats: dict, title: str = "Session stats") -> None:
    total_rounds = stats["total_rounds"]
    total_attempts = stats["total_attempts"]
    total_skipped = stats["skipped"]
    per_feature = stats["per_feature"]
    missed_words = stats["missed_words"]
    attempts_per_word = stats["attempts_per_word"]
    if total_rounds == 0:
        print("No rounds played.")
        return
    avg_attempts = total_attempts / total_rounds
    print(f"\n{title}")
    print(f"Total rounds: {total_rounds}")
    print(f"Correct: {stats['correct']}")
    print(f"Skipped: {total_skipped}")
    print(f"Average attempts per round: {avg_attempts:.2f}")
    print("Per-feature accuracy:")
    for feature, stats in per_feature.items():
        rounds = stats["rounds"]
        correct = stats["correct"]
        if rounds == 0:
            continue
        accuracy = (correct / rounds) * 100
        print(f"- {feature}: {accuracy:.1f}% ({correct}/{rounds})")
    if missed_words:
        print("Most missed words:")
        for word, count in sorted(missed_words.items(), key=lambda item: item[1], reverse=True)[:5]:
            print(f"- {word}: {count}")
    if attempts_per_word:
        print("Attempts per word (top 5 by avg attempts):")
        ordered = sorted(
            attempts_per_word.items(),
            key=lambda item: item[1]["attempts"] / item[1]["rounds"],
            reverse=True,
        )[:5]
        for word, data in ordered:
            avg_word_attempts = data["attempts"] / data["rounds"]
            print(f"- {word}: {avg_word_attempts:.2f} avg over {data['rounds']} rounds")


def build_missed_words_pool(words: list[dict], missed_words: dict[str, int]) -> list[dict]:
    pool: list[dict] = []
    for word in words:
        text = word.get("text", "<missing>")
        repeats = missed_words.get(text, 0)
        if repeats > 0:
            pool.extend([word] * repeats)
    return pool


def print_firestore_setup_notes() -> None:
    print("Firestore setup notes:")
    print("- Install firebase-admin: pip install firebase-admin")
    print("- Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON,")
    print("  or pass --service-account path\\to\\service_account.json")
    print("- Optional: pass --firestore-project your-project-id")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pronunciation feature quiz")
    parser.add_argument(
        "--dataset",
        choices=["json", "firestore"],
        default="json",
        help="Data source: json or firestore (default: json)",
    )
    parser.add_argument(
        "--json-path",
        default="test_words.json",
        help="Path to JSON dataset (default: test_words.json)",
    )
    parser.add_argument(
        "--firestore-collection",
        default="words",
        help="Firestore collection name (default: words)",
    )
    parser.add_argument(
        "--firestore-project",
        default=None,
        help="Firestore project ID (optional)",
    )
    parser.add_argument(
        "--firestore-limit",
        type=int,
        default=None,
        help="Limit number of Firestore docs (optional)",
    )
    parser.add_argument(
        "--firestore-order-by",
        default=None,
        help="Order Firestore docs by field (optional)",
    )
    parser.add_argument(
        "--firestore-order-dir",
        choices=["asc", "desc"],
        default="asc",
        help="Order direction for Firestore query (default: asc)",
    )
    parser.add_argument(
        "--firestore-start-after",
        default=None,
        help="Start after a document ID (optional)",
    )
    parser.add_argument(
        "--clip-url-field",
        default="clip_url",
        help="Firestore field for clip URL (default: clip_url)",
    )
    parser.add_argument(
        "--open-clip",
        action="store_true",
        help="Open clip location in the default browser/player",
    )
    parser.add_argument(
        "--service-account",
        default=None,
        help="Path to Firebase service account JSON (optional)",
    )
    parser.add_argument(
        "--clips-dir",
        default="clips",
        help="Directory containing clip files (default: clips)",
    )
    parser.add_argument(
        "--clip-template",
        default="{clip_id}.mp4",
        help="Clip filename template (default: {clip_id}.mp4)",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    if args.dataset == "json":
        json_path = (base_dir / args.json_path).resolve()
        words = load_words(json_path)
        print(f"Loaded {len(words)} words from {json_path.name}.")
    else:
        try:
            words = load_words_firestore(
                args.firestore_collection,
                args.firestore_project,
                args.service_account,
                args.firestore_limit,
                args.firestore_order_by,
                args.firestore_order_dir,
                args.firestore_start_after,
            )
        except RuntimeError as exc:
            print(str(exc))
            print_firestore_setup_notes()
            return
        if not words:
            print("No words found in Firestore collection.")
            return
        print(f"Loaded {len(words)} words from Firestore.")

    stats = init_stats()

    while True:
        attempts, wrong_guesses, skipped, correct, feature, text, did_quit = run_round(
            words,
            base_dir,
            args.clips_dir,
            args.clip_template,
            args.clip_url_field,
            args.open_clip,
        )
        if did_quit:
            break
        update_stats(stats, attempts, wrong_guesses, skipped, correct, feature, text)

    print_stats(stats)

    if stats["missed_words"]:
        review = input("Review missed words now? (y/n): ").strip().lower()
        if review in {"y", "yes"}:
            missed_pool = build_missed_words_pool(words, stats["missed_words"])
            if not missed_pool:
                print("No missed words available for review.")
                return
            random.shuffle(missed_pool)
            print(f"Reviewing {len(missed_pool)} missed items (one pass)...")
            review_stats = init_stats()
            for word in missed_pool:
                attempts, wrong_guesses, skipped, correct, feature, text, did_quit = run_round(
                    [word],
                    base_dir,
                    args.clips_dir,
                    args.clip_template,
                    args.clip_url_field,
                    args.open_clip,
                )
                if did_quit:
                    break
                update_stats(review_stats, attempts, wrong_guesses, skipped, correct, feature, text)
            print_stats(review_stats, title="Review stats")


if __name__ == "__main__":
    main()
