#!/usr/bin/env python3
import os
import re
import sys
import json
import urllib.request
import urllib.error
import curses

# Regex matching t{x}w{y}-{z} where x and y are alphanumeric, and z is any word/hyphen character
REPO_PATTERN = re.compile(r'^t[a-zA-Z0-9]+w[a-zA-Z0-9]+-[a-zA-Z0-9_-]+$')

def github_request(url, token, data=None, method='GET'):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'token {token}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('User-Agent', 'Python-Greenery-Script')
    
    if data is not None:
        req.add_header('Content-Type', 'application/json')
        json_data = json.dumps(data).encode('utf-8')
    else:
        json_data = None
        
    try:
        with urllib.request.urlopen(req, data=json_data) as response:
            link_header = response.headers.get('Link', '')
            body = response.read().decode('utf-8')
            return json.loads(body) if body else {}, link_header
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        raise Exception(f"HTTP Error {e.code}: {error_msg}")
    except urllib.error.URLError as e:
        raise Exception(f"URL Error: {e.reason}")

def get_all_repositories(token, progress_callback=None):
    repos = []
    page = 1
    while True:
        if progress_callback:
            progress_callback(page)
        # Fetching repos where the user is an owner
        url = f"https://api.github.com/user/repos?visibility=all&affiliation=owner&per_page=100&page={page}"
        page_repos, link_header = github_request(url, token)
        if not page_repos:
            break
        repos.extend(page_repos)
        
        # Check Link header for next page
        if 'rel="next"' not in link_header:
            break
        page += 1
        
    return repos

def make_repo_private(owner, repo_name, token):
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    data = {"private": True}
    github_request(url, token, data=data, method='PATCH')

def transfer_repo_ownership(owner, repo_name, new_owner, token):
    url = f"https://api.github.com/repos/{owner}/{repo_name}/transfer"
    data = {"new_owner": new_owner}
    github_request(url, token, data=data, method='POST')

def run_tui(stdscr, token):
    # Hide cursor
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    # Colors
    curses.start_color()
    curses.use_default_colors()
    # Active/Selected highlight: White text, Blue background
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    # Status / Info messages: Green text
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    # Errors: Red text
    curses.init_pair(3, curses.COLOR_RED, -1)
    # Private tag: Yellow text
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    # Selected checkbox: Green text
    curses.init_pair(5, curses.COLOR_GREEN, -1)

    repos = []
    status_msg = "Fetching repositories..."
    status_color = 2
    
    def draw_status(msg, color_pair=2):
        nonlocal status_msg, status_color
        status_msg = msg
        status_color = color_pair

    def update_progress(page):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        msg = f"Fetching GitHub repositories (Page {page})..."
        stdscr.addstr(h // 2, max(0, (w - len(msg)) // 2), msg, curses.A_BOLD)
        stdscr.refresh()

    try:
        repos_raw = get_all_repositories(token, progress_callback=update_progress)
        # Add a local 'selected' attribute to track checkboxes
        repos = []
        for r in repos_raw:
            repos.append({
                "name": r.get("name"),
                "owner": r.get("owner", {}).get("login"),
                "private": r.get("private", False),
                "selected": False
            })
        draw_status(f"Loaded {len(repos)} repositories successfully.")
    except Exception as e:
        draw_status(f"Error fetching repositories: {e}", 3)

    cursor_idx = 0
    scroll_top = 0
    filter_query = ""
    filter_mode = "substring" # "substring", "pattern" (regex), "none"

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # 1. Filter the repository list
        filtered_repos = []
        for r in repos:
            if filter_mode == "substring":
                if filter_query.lower() in r["name"].lower():
                    filtered_repos.append(r)
            elif filter_mode == "pattern":
                if REPO_PATTERN.match(r["name"]):
                    filtered_repos.append(r)
            else:
                filtered_repos.append(r)

        # Bounds checks
        if not filtered_repos:
            cursor_idx = 0
        elif cursor_idx >= len(filtered_repos):
            cursor_idx = len(filtered_repos) - 1
        elif cursor_idx < 0:
            cursor_idx = 0

        # Draw Header
        title = " 🌿 Greenery Repository Manager "
        stdscr.addstr(0, 0, title.center(w), curses.A_REVERSE)
        
        filter_display = "All"
        if filter_mode == "substring" and filter_query:
            filter_display = f"Substring: '{filter_query}'"
        elif filter_mode == "pattern":
            filter_display = "Regex Pattern: 'tXwY-Z'"
            
        header_info = f" Filter: {filter_display} | Match Count: {len(filtered_repos)} / {len(repos)}"
        stdscr.addstr(1, 0, header_info[:w-1])
        stdscr.addstr(2, 0, "-" * w)

        # Draw List
        list_height = h - 7  # Reserved lines for header and footer panels
        if list_height > 0:
            # Adjust scroll window
            if cursor_idx < scroll_top:
                scroll_top = cursor_idx
            elif cursor_idx >= scroll_top + list_height:
                scroll_top = cursor_idx - list_height + 1

            for idx in range(list_height):
                item_idx = scroll_top + idx
                if item_idx >= len(filtered_repos):
                    break
                
                r = filtered_repos[item_idx]
                line_y = 3 + idx
                
                # Format: [ ] or [x]
                chk = "[x]" if r["selected"] else "[ ]"
                chk_color = curses.color_pair(5) if r["selected"] else curses.A_NORMAL
                
                # Visibility badge
                vis_badge = "[Private]" if r["private"] else "[Public]"
                vis_color = curses.color_pair(4) if r["private"] else curses.A_NORMAL
                
                repo_label = f" {chk} {vis_badge:<9} {r['owner']}/{r['name']}"
                # Truncate if it exceeds width
                repo_label = repo_label[:w-1]
                
                is_current = (item_idx == cursor_idx)
                
                if is_current:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(line_y, 0, repo_label.ljust(w-1))
                    stdscr.attroff(curses.color_pair(1))
                else:
                    # Draw check box
                    stdscr.addstr(line_y, 1, chk, chk_color)
                    # Draw visibility badge
                    stdscr.addstr(line_y, 5, vis_badge, vis_color)
                    # Draw name
                    stdscr.addstr(line_y, 15, f"{r['owner']}/{r['name']}")

        # Draw Footer / Status Pane
        footer_start_y = h - 4
        if footer_start_y > 2:
            stdscr.addstr(footer_start_y, 0, "-" * w)
            
            # Status line
            stdscr.addstr(footer_start_y + 1, 0, " Status: ")
            stdscr.addstr(footer_start_y + 1, 9, status_msg[:w-10], curses.color_pair(status_color) | curses.A_BOLD)
            
            # Key guides
            guide1 = "[Space] Toggle | [f] Filter Name | [m] Pattern Match | [c] Clear Filter | [a] Select All"
            guide2 = "[p] Make Private | [t] Transfer to axion-au | [q] Quit | [Up/Down] Navigate"
            stdscr.addstr(footer_start_y + 2, 0, guide1[:w-1])
            stdscr.addstr(footer_start_y + 3, 0, guide2[:w-1])

        stdscr.refresh()

        # Handle input
        key = stdscr.getch()

        if key == ord('q'):
            break

        elif key in (curses.KEY_UP, ord('k')):
            cursor_idx -= 1

        elif key in (curses.KEY_DOWN, ord('j')):
            cursor_idx += 1

        elif key == ord(' '):
            if filtered_repos:
                filtered_repos[cursor_idx]["selected"] = not filtered_repos[cursor_idx]["selected"]

        elif key == ord('f'):
            # Text filter input mode
            curses.curs_set(1)
            stdscr.addstr(1, 0, " Enter filter query: ".ljust(w), curses.A_REVERSE)
            stdscr.refresh()
            
            input_query = []
            while True:
                # Refresh input display line
                stdscr.move(1, 20)
                stdscr.clrtoeol()
                stdscr.addstr(1, 20, "".join(input_query))
                stdscr.refresh()
                
                ch = stdscr.getch()
                if ch in (10, 13): # Enter
                    break
                elif ch == 27: # Escape
                    input_query = None
                    break
                elif ch in (curses.KEY_BACKSPACE, 127, 8):
                    if input_query:
                        input_query.pop()
                elif 32 <= ch <= 126:
                    input_query.append(chr(ch))
            
            curses.curs_set(0)
            if input_query is not None:
                filter_query = "".join(input_query)
                filter_mode = "substring"
                cursor_idx = 0
                draw_status(f"Filter set to: '{filter_query}'")
            else:
                draw_status("Filter entry cancelled.")

        elif key == ord('m'):
            filter_mode = "pattern"
            cursor_idx = 0
            draw_status("Filtered by standard regex pattern: 'tXwY-Z'")

        elif key == ord('c'):
            filter_mode = "substring"
            filter_query = ""
            cursor_idx = 0
            draw_status("Filters cleared.")

        elif key == ord('a'):
            count = 0
            for r in filtered_repos:
                if not r["private"]:
                    r["selected"] = True
                    count += 1
            draw_status(f"Selected all matching public repositories ({count} repos).")

        elif key == ord('u'):
            count = 0
            for r in filtered_repos:
                if r["selected"]:
                    r["selected"] = False
                    count += 1
            draw_status(f"Deselected all matching repositories ({count} repos).")

        elif key == ord('p'):
            # Bulk action: Make private
            selected_repos = [r for r in repos if r["selected"] and not r["private"]]
            if not selected_repos:
                draw_status("No public repositories selected for visibility update.", 3)
                continue
            
            # Confirm confirmation prompt
            confirm_msg = f"Make {len(selected_repos)} repositories private? (y/n): "
            stdscr.move(footer_start_y + 1, 0)
            stdscr.clrtoeol()
            stdscr.addstr(footer_start_y + 1, 0, confirm_msg, curses.A_BOLD)
            stdscr.refresh()
            
            conf_key = stdscr.getch()
            if conf_key not in (ord('y'), ord('Y')):
                draw_status("Bulk update cancelled.")
                continue
            
            # Process updates
            success = 0
            failed = 0
            for i, r in enumerate(selected_repos):
                draw_status(f"Updating [{i+1}/{len(selected_repos)}]: {r['name']}...", 2)
                stdscr.clear() # Force redrawing layout
                # Re-render status line during progress
                stdscr.addstr(footer_start_y + 1, 0, f" Status: Updating {r['owner']}/{r['name']}...".ljust(w), curses.color_pair(2) | curses.A_BOLD)
                stdscr.refresh()
                try:
                    make_repo_private(r["owner"], r["name"], token)
                    r["private"] = True
                    r["selected"] = False
                    success += 1
                except Exception as e:
                    failed += 1
            
            draw_status(f"Finished bulk update: {success} succeeded, {failed} failed.")

        elif key == ord('t'):
            # Bulk action: Transfer ownership to axion-au
            selected_repos = [r for r in repos if r["selected"]]
            if not selected_repos:
                draw_status("No repositories selected for ownership transfer.", 3)
                continue
            
            # Confirm confirmation prompt
            confirm_msg = f"Transfer {len(selected_repos)} repos to 'axion-au'? (y/n): "
            stdscr.move(footer_start_y + 1, 0)
            stdscr.clrtoeol()
            stdscr.addstr(footer_start_y + 1, 0, confirm_msg, curses.A_BOLD)
            stdscr.refresh()
            
            conf_key = stdscr.getch()
            if conf_key not in (ord('y'), ord('Y')):
                draw_status("Transfer cancelled.")
                continue
            
            # Process updates
            success = 0
            failed = 0
            for i, r in enumerate(selected_repos):
                draw_status(f"Transferring [{i+1}/{len(selected_repos)}]: {r['name']}...", 2)
                stdscr.clear() # Force redrawing layout
                stdscr.addstr(footer_start_y + 1, 0, f" Status: Transferring {r['owner']}/{r['name']} to axion-au...".ljust(w), curses.color_pair(2) | curses.A_BOLD)
                stdscr.refresh()
                try:
                    transfer_repo_ownership(r["owner"], r["name"], "axion-au", token)
                    r["owner"] = "axion-au"
                    r["selected"] = False
                    success += 1
                except Exception as e:
                    failed += 1
            
            draw_status(f"Finished transfer: {success} succeeded, {failed} failed.")

def main():
    # Load .env file if it exists
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key, val = parts[0].strip(), parts[1].strip()
                        # Strip optional quotes around value
                        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                            val = val[1:-1]
                        os.environ[key] = val

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN is not set in environment or .env file.", file=sys.stderr)
        sys.exit(1)
        
    # Check if we should fallback or run TUI
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print("Usage: python3 make_private.py [options]")
        print("Runs the interactive Repository Manager TUI by default.")
        sys.exit(0)

    try:
        curses.wrapper(run_tui, token)
    except KeyboardInterrupt:
        print("\nExiting TUI...")
        sys.exit(0)
    except Exception as e:
        print(f"\nTUI Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
