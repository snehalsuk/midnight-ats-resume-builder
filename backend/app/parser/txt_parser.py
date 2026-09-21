def extract_lines_from_txt(file_bytes: bytes) -> list[str]:
    text = file_bytes.decode("utf-8", errors="ignore")
    return [line.strip() for line in text.split("\n") if line.strip()]
