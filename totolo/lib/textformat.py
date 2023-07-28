import textwrap


def remove_wordwrap(text):
    """
    Remove single newline characters (i.e. '\n') from string, but leave double
    newlines (i.e. '\n\n').
    """
    text_blocks = text.split("\n")
    dewordwraped_text_block = []
    dewordwraped_text_blocks = []

    for text_block in text_blocks:
        text_block = text_block.strip()

        if not text_block:
            if dewordwraped_text_block:
                dewordwraped_text_blocks.append(" ".join(dewordwraped_text_block))
            dewordwraped_text_block = []
        else:
            dewordwraped_text_block.append(text_block)

    if dewordwraped_text_block:
        dewordwraped_text_blocks.append(" ".join(dewordwraped_text_block))

    return "\n\n".join(dewordwraped_text_blocks)


def add_wordwrap(text, wrap_length=78):
    """
    Add line breaks to string (i.e. '\\n' character) so that each line is at
    most 'wrap_length' characters in length.
    """
    paragraphs = remove_wordwrap(text)
    wordwrapped_lines = []

    for paragraph in paragraphs.split("\n\n"):
        for wordwrapped_line in textwrap.fill(paragraph, wrap_length).split("\n"):
            wordwrapped_lines.append(wordwrapped_line.strip())
        wordwrapped_lines.append("")

    return "\n".join(wordwrapped_lines)
