
import re
import unicodedata


def normalize_text(text):
    text = unicodedata.normalize("NFC", text)
    return text


def tokenize(text):
    text = normalize_text(text)

    words = re.findall(
        r'[\u0C00-\u0C7F]+|[a-zA-Z]+|\d+',
        text
    )

    return words


def get_positions(words):
    word_positions = {}

    for i in range(len(words)):
        word = words[i]

        if word not in word_positions:
            word_positions[word] = []

        word_positions[word].append(i + 1)

    return word_positions


def preprocess_document(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    words = tokenize(text)

    return words


if __name__ == "__main__":

    text = "భారతదేశం ఒక అందమైన దేశం భారతదేశం"

    print("Original Text:")
    print(text)

    words = tokenize(text)

    print("\nAfter Tokenization:")
    print(words)

    print("\nWord Positions:")

    positions = get_positions(words)

    for word in positions:
        print(word, ":", positions[word])
