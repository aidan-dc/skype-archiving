from utils import *

def main():
    data     = pd.read_json(JSON_FILE)
    convos   = extract_chats(data, MY_NAME)
    md_files = save_as_markdown(convos, OUTPUT_DIR)
    if CONVERT_PDF:
        convert_md_to_pdf(md_files)

if __name__ == "__main__":
    # Update this with your actual file
    JSON_FILE   = "messages.json"  
    # Where the chats will be saved
    OUTPUT_DIR  = "chats"
    # Input the name to be used in your own sent chats
    MY_NAME     = "Aidan Chambers"
    # Optional conversion from markdown to pdf, requires pandoc
    CONVERT_PDF = False

    # Ensure output directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main()