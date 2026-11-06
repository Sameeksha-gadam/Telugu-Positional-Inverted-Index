
import bz2
import os
import csv
import re
import xml.etree.ElementTree as ET
import mwparserfromhell


project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dataset_folder = os.path.join(project_folder, "dataset")
output_folder = os.path.join(dataset_folder, "extracted_articles")

max_articles = 500


def get_tag_name(tag):
    return tag.split("}")[-1]


def clean_article(text):
    wiki_text = mwparserfromhell.parse(text)
    text = wiki_text.strip_code()

    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def count_telugu_words(text):
    count = 0

    for character in text:
        if "\u0C00" <= character <= "\u0C7F":
            count += 1

    return count


def extract_articles():

    os.makedirs(output_folder, exist_ok=True)

    dump_file = os.path.join(
        dataset_folder,
        "tewiki-latest-pages-articles.xml.bz2"
    )

    if not os.path.exists(dump_file):
        print("Wikipedia dump file not found!")
        return

    article_count = 0
    skipped_count = 0

    metadata_file = os.path.join(output_folder, "metadata.csv")

    print("Starting Telugu Wikipedia extraction...")
    print("Please wait...\n")

    with bz2.open(dump_file, "rb") as file:

        with open(metadata_file, "w", newline="", encoding="utf-8-sig") as csvfile:

            writer = csv.writer(csvfile)
            writer.writerow(["Document ID", "Article Title", "File Name"])

            elements = ET.iterparse(file, events=("start", "end"))
            element_stack = []

            for event, element in elements:

                if event == "start":
                    element_stack.append(element)
                    continue

                if get_tag_name(element.tag) == "page":

                    title = ""
                    namespace = ""
                    raw_text = ""

                    for child in element:

                        tag = get_tag_name(child.tag)

                        if tag == "title":
                            title = child.text or ""

                        elif tag == "ns":
                            namespace = child.text or ""

                        elif tag == "revision":

                            for revision_child in child.iter():

                                if get_tag_name(revision_child.tag) == "text":
                                    raw_text = revision_child.text or ""
                                    break

                    if namespace == "0" and raw_text:

                        is_redirect = any(
                            get_tag_name(child.tag) == "redirect"
                            for child in element
                        )

                        if not is_redirect:

                            article_text = clean_article(raw_text)

                            if (
                                len(article_text) >= 100
                                and count_telugu_words(article_text) >= 30
                            ):

                                article_count += 1

                                document_id = "D" + str(article_count)
                                file_name = document_id + ".txt"

                                file_path = os.path.join(
                                    output_folder,
                                    file_name
                                )

                                with open(
                                    file_path,
                                    "w",
                                    encoding="utf-8"
                                ) as article_file:

                                    article_file.write(article_text)

                                writer.writerow([
                                    document_id,
                                    title,
                                    file_name
                                ])

                                if article_count % 25 == 0:
                                    print(
                                        "Articles extracted:",
                                        article_count
                                    )

                            else:
                                skipped_count += 1

                        else:
                            skipped_count += 1

                    else:
                        skipped_count += 1

                    if len(element_stack) > 1:
                        parent = element_stack[-2]
                        parent.remove(element)

                    element.clear()

                    if article_count >= max_articles:
                        break

                element_stack.pop()

    print("\nExtraction completed!")
    print("----------------------")
    print("Total articles extracted:", article_count)
    print("Pages skipped:", skipped_count)
    print("Saved articles in:", output_folder)
    print("Metadata saved in:", metadata_file)


if __name__ == "__main__":
    extract_articles()
