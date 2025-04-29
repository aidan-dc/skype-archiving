import pandas as pd
import os
from datetime import datetime
import re
import textwrap

def format_text_for_markdown(text, width=32):
    """
    Apply all necessary formatting:
    - Escape special LaTeX characters
    - Replace newlines with Markdown-friendly breaks
    - Wrap long words & URLs to prevent overflow
    """
    # Escape LaTeX special characters
    special_chars = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "\\": r"\\",
    }
    for char, escaped in special_chars.items():
        text = text.replace(char, escaped)

    # Fix line breaks: Convert `\n` to Markdown-style line breaks
    text = text.replace("\n", "  \n")  # Markdown requires double spaces for a line break

    # Ensure long URLs & words wrap by adding soft breakpoints
    text = re.sub(r'(\w{20,})', lambda m: textwrap.fill(m.group(0), width=width, break_long_words=True), text)
    text = re.sub(r'(?<=/)', '\u200B', text)  # Insert zero-width space after slashes for URL wrapping

    return text


def extract_chats(data, skipBlocked = True):
    """
    Extract messages grouped by conversation.
    """
    convos = {}

    for i, row in data.iterrows():
        temp = row['conversations']
        if skipBlocked and temp['properties']['conversationblocked']:
            continue # Skip blocked conversations
        if len(temp['MessageList'])<1 or temp['id'] == '48:calllogs':
            continue # Skip empty conversations or call logs

        displayName = temp['displayName']

        if displayName not in convos:
            convos[displayName] = []

        messageList = temp['MessageList']
        for m in messageList:
            timestamp  = m['originalarrivaltime']
            senderName = m['displayName']
            if row['userId']==m['from']:
                senderName = MY_NAME
            content    = m['content']


            # Convert timestamp to sortable format
            try:
                timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                timestamp = datetime.min  # Fallback if timestamp parsing fails

            convos[displayName].append((timestamp, f"**{str(timestamp)[:16]} - {senderName}**: {content}"))

    for chat_id in convos:
        convos[chat_id].sort()  # Sorts by timestamp (first element of tuple)
        convos[chat_id] = [msg[1] for msg in convos[chat_id]]  # Remove timestamps for clean output

    return convos

def save_as_markdown(convos):
    """
    Save each conversation as a Markdown file.
    """
    md_files = []
    for chat_id, messages in convos.items():
        filename = os.path.join(OUTPUT_DIR, f"{chat_id}.md")
        with open(filename, "w", encoding="utf-8") as f:
            formatted_messages = [format_text_for_markdown(m) for m in messages]
            f.write(f"# Chat: {chat_id}\n\n" + "\n\n".join(formatted_messages))
        md_files.append(filename)
    return md_files

def convert_md_to_pdf(md_files):
    """
    Convert Markdown files to PDF using Pandoc, handling Unicode and improving formatting.
    Messy, intended for MacOS systems and requires Pandoc
    """
    for md_file in md_files:
        if not os.path.exists(md_file):
            print(f"Error: File not found -> {md_file}")
            continue

        pdf_filename = md_file.replace(".md", ".pdf")

        # Ensure UTF-8 encoding to prevent Unicode errors
        with open(md_file, "r", encoding="utf-8", errors="replace") as f:
            md_content = f.read()

        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        os.system(f'pandoc -f markdown --pdf-engine=xelatex '
          f'-V geometry:margin=0.5in -V mainfont="Arial" '
          f'-V fontsize=12pt -V linestretch=1.5 '
          f'-V ragged-right -V breakurl=true -V hyphenate=true'
          f'--wrap=auto "{md_file}" -o "{pdf_filename}"')

        print(f"Saved PDF: {pdf_filename}")

def main():
    data     = pd.read_json(JSON_FILE)
    convos   = extract_chats(data)
    md_files = save_as_markdown(convos)
    if CONVERT_PDF:
        convert_md_to_pdf(md_files)

if __name__ == "__main__":
    JSON_FILE   = "messages.json"  # Update this with your actual file
    OUTPUT_DIR  = "chats"          # Where the chats will be saved
    MY_NAME     = "Aidan Chambers"
    CONVERT_PDF = False

    # Ensure output directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main()