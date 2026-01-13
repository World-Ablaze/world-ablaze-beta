"""
Delete naval cheat events from WA_AI_CHEATS_*.txt files.
Removes entire country_event blocks by event ID.
"""

import re
from pathlib import Path
from typing import List, Tuple

EVENTS_TO_DELETE = {
    'WA_AI_CHEATS_GER.txt': [
        'ger_armor.907',  # Final GER naval event
        'ger_armor.945',  # Final GER naval event
    ],
    'WA_AI_CHEATS_USA.txt': [
        'usa_armor.901',  # Final USA naval event
    ],
    'WA_AI_CHEATS_JAP.txt': [
        'jap_armor.604',  # Final JAP naval event
    ],
}

def find_event_block(content: str, event_id: str) -> Tuple[int, int]:
    """Find start and end positions of an event block by ID."""
    # Find the event ID line
    pattern = rf'id\s*=\s*{re.escape(event_id)}\b'
    match = re.search(pattern, content)

    if not match:
        return -1, -1

    id_pos = match.start()

    # Search backwards for country_event {
    search_start = max(0, id_pos - 5000)
    before_content = content[search_start:id_pos]

    # Find last country_event before id
    event_start_pattern = r'country_event\s*=?\s*\{'
    matches = list(re.finditer(event_start_pattern, before_content))

    if not matches:
        return -1, -1

    last_match = matches[-1]
    event_start = search_start + last_match.start()

    # Find matching closing brace
    brace_count = 0
    in_block = False

    for i, char in enumerate(content[event_start:]):
        if char == '{':
            brace_count += 1
            in_block = True
        elif char == '}':
            brace_count -= 1
            if in_block and brace_count == 0:
                event_end = event_start + i + 1
                return event_start, event_end

    return event_start, len(content)

def delete_events_from_file(filepath: Path, event_ids: List[str], dry_run: bool = False) -> Tuple[int, List[str]]:
    """Delete event blocks from a file."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    original_content = content
    messages = []
    deleted_count = 0

    # Sort event IDs to delete from end to start (to maintain positions)
    events_with_positions = []
    for event_id in event_ids:
        start, end = find_event_block(content, event_id)
        if start != -1:
            events_with_positions.append((start, end, event_id))
        else:
            messages.append(f"  WARNING: Event {event_id} not found")

    # Sort by start position (descending) to delete from end
    events_with_positions.sort(key=lambda x: x[0], reverse=True)

    # Delete events
    for start, end, event_id in events_with_positions:
        # Remove the event block and any trailing blank lines
        while end < len(content) and content[end] in '\n\r':
            end += 1

        content = content[:start] + content[end:]
        deleted_count += 1
        messages.append(f"  Deleted: {event_id} ({end - start} bytes)")

    # Write changes
    if content != original_content and not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return deleted_count, messages

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Delete naval cheat events from WA_AI_CHEATS files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted')
    args = parser.parse_args()

    base_path = Path(__file__).parent.parent
    events_path = base_path / 'events'

    total_deleted = 0

    print("Deleting naval cheat events...")
    if args.dry_run:
        print("(DRY RUN - no changes will be made)")
    print()

    for filename, event_ids in EVENTS_TO_DELETE.items():
        filepath = events_path / filename

        if not filepath.exists():
            print(f"{filename}: NOT FOUND")
            continue

        deleted, messages = delete_events_from_file(filepath, event_ids, args.dry_run)

        print(f"{filename}: {deleted} events deleted")
        for msg in messages:
            print(msg)
        print()

        total_deleted += deleted

    print(f"Total: {total_deleted} events deleted")

if __name__ == '__main__':
    main()
