#!/usr/bin/env python3
"""Generate small test dataset with partitioning applied."""

import random
import os

# Small dataset for testing
USERS_NUM = 100
ARTICLES_NUM = 50
READS_NUM = 500

uid_region = {}
aid_category = {}


def gen_user_values(i):
    """Generate user record values."""
    timeBegin = 1506328859000
    user_id = f"u{i}"
    uid = str(i)
    name = f"user{i}"
    gender = "male" if random.random() > 0.33 else "female"
    email = f"email{i}"
    phone = f"phone{i}"
    dept = f"dept{int(random.random() * 20)}"
    grade = f"grade{int(random.random() * 4 + 1)}"
    language = "en" if random.random() > 0.8 else "zh"
    region = "Beijing" if random.random() > 0.4 else "Hong Kong"
    role = f"role{int(random.random() * 3)}"
    preferTags = f"tags{int(random.random() * 50)}"
    obtainedCredits = str(int(random.random() * 100))

    uid_region[uid] = region

    return (
        f"('{timeBegin + i}', '{user_id}', '{uid}', '{name}', '{gender}', "
        f"'{email}', '{phone}', '{dept}', '{grade}', '{language}', "
        f"'{region}', '{role}', '{preferTags}', '{obtainedCredits}')"
    )


def gen_article_values(i):
    """Generate article record values."""
    timeBegin = 1506000000000
    article_id = f"a{i}"
    aid = str(i)
    title = f"title{i}"
    category = "science" if random.random() > 0.55 else "technology"
    abstract = f"abstract of article {i}"
    articleTags = f"tags{int(random.random() * 50)}"
    authors = f"author{int(random.random() * 100)}"
    language = "en" if random.random() > 0.5 else "zh"

    # Store file paths (will upload to MinIO later)
    text = f"articles/article{i}/text_a{i}.txt"
    image = f"articles/article{i}/image_a{i}_0.jpg"
    video = f"articles/article{i}/video_a{i}.flv" if random.random() < 0.05 else ""

    aid_category[aid] = category

    return (
        f"('{timeBegin + i}', '{article_id}', '{aid}', '{title}', '{category}', "
        f"'{abstract}', '{articleTags}', '{authors}', '{language}', "
        f"'{text}', '{image}', '{video}')"
    )


def gen_read_values(i):
    """Generate read record values."""
    timeBegin = 1506332297000
    read_id = f"r{i}"
    uid = str(int(random.random() * USERS_NUM))
    aid = str(int(random.random() * ARTICLES_NUM))

    # Check if user would read this article based on region/language
    region = uid_region.get(uid, "Beijing")

    readTimeLength = str(int(random.random() * 100))
    agreeOrNot = "1" if random.random() < 0.3 else "0"
    commentOrNot = "1" if random.random() < 0.2 else "0"
    shareOrNot = "1" if random.random() < 0.1 else "0"
    commentDetail = f"comment {i} on article {aid}"

    return (
        f"('{timeBegin + i * 10000}', '{read_id}', '{uid}', '{aid}', "
        f"'{readTimeLength}', '{agreeOrNot}', '{commentOrNot}', '{shareOrNot}', "
        f"'{commentDetail}')"
    )


def generate_partitioned_sql():
    """Generate SQL files with partitioning applied."""
    print("Generating partitioned SQL files...")

    # Create output directory
    os.makedirs("generated_data", exist_ok=True)

    # Generate users with partitioning
    print(f"Generating {USERS_NUM} users...")
    beijing_users = []
    hongkong_users = []

    for i in range(USERS_NUM):
        values = gen_user_values(i)
        region = uid_region[str(i)]

        if region == "Beijing":
            beijing_users.append(values)
        else:
            hongkong_users.append(values)

    # Write user SQL for DBMS1 (Beijing)
    with open("generated_data/user_dbms1.sql", "w") as f:
        f.write("-- Users for DBMS1 (Beijing)\n")
        if beijing_users:
            f.write('INSERT INTO "user" (timestamp, id, uid, name, gender, email, phone, dept, grade, language, region, role, preferTags, obtainedCredits) VALUES\n')
            f.write(",\n".join(beijing_users))
            f.write(";\n")

    # Write user SQL for DBMS2 (Hong Kong)
    with open("generated_data/user_dbms2.sql", "w") as f:
        f.write("-- Users for DBMS2 (Hong Kong)\n")
        if hongkong_users:
            f.write('INSERT INTO "user" (timestamp, id, uid, name, gender, email, phone, dept, grade, language, region, role, preferTags, obtainedCredits) VALUES\n')
            f.write(",\n".join(hongkong_users))
            f.write(";\n")

    print(f"  Beijing users: {len(beijing_users)}, Hong Kong users: {len(hongkong_users)}")

    # Generate articles with partitioning
    print(f"Generating {ARTICLES_NUM} articles...")
    science_articles = []
    tech_articles = []

    for i in range(ARTICLES_NUM):
        values = gen_article_values(i)
        category = aid_category[str(i)]

        if category == "science":
            science_articles.append(values)
        else:
            tech_articles.append(values)

    # Write article SQL for DBMS1 (science articles - replicated)
    with open("generated_data/article_dbms1.sql", "w") as f:
        f.write("-- Articles for DBMS1 (science only, replicated)\n")
        if science_articles:
            f.write('INSERT INTO "article" (timestamp, id, aid, title, category, abstract, articleTags, authors, language, text, image, video) VALUES\n')
            f.write(",\n".join(science_articles))
            f.write(";\n")

    # Write article SQL for DBMS2 (all articles: science + technology)
    with open("generated_data/article_dbms2.sql", "w") as f:
        f.write("-- Articles for DBMS2 (science + technology)\n")
        all_articles = science_articles + tech_articles
        if all_articles:
            f.write('INSERT INTO "article" (timestamp, id, aid, title, category, abstract, articleTags, authors, language, text, image, video) VALUES\n')
            f.write(",\n".join(all_articles))
            f.write(";\n")

    print(f"  Science articles: {len(science_articles)}, Technology articles: {len(tech_articles)}")

    # Generate reads with co-location
    print(f"Generating {READS_NUM} reads...")
    beijing_reads = []
    hongkong_reads = []

    for i in range(READS_NUM):
        values = gen_read_values(i)
        # Extract uid to determine region
        uid = str(int(random.random() * USERS_NUM))
        region = uid_region.get(uid, "Beijing")

        if region == "Beijing":
            beijing_reads.append(values)
        else:
            hongkong_reads.append(values)

    # Write read SQL for DBMS1 (Beijing users' reads)
    with open("generated_data/read_dbms1.sql", "w") as f:
        f.write("-- Reads for DBMS1 (Beijing users)\n")
        if beijing_reads:
            f.write('INSERT INTO "user_read" (timestamp, id, uid, aid, readTimeLength, agreeOrNot, commentOrNot, shareOrNot, commentDetail) VALUES\n')
            f.write(",\n".join(beijing_reads))
            f.write(";\n")

    # Write read SQL for DBMS2 (Hong Kong users' reads)
    with open("generated_data/read_dbms2.sql", "w") as f:
        f.write("-- Reads for DBMS2 (Hong Kong users)\n")
        if hongkong_reads:
            f.write('INSERT INTO "user_read" (timestamp, id, uid, aid, readTimeLength, agreeOrNot, commentOrNot, shareOrNot, commentDetail) VALUES\n')
            f.write(",\n".join(hongkong_reads))
            f.write(";\n")

    print(f"  Beijing reads: {len(beijing_reads)}, Hong Kong reads: {len(hongkong_reads)}")

    print("\n✓ SQL files generated in generated_data/ directory")
    print("  - user_dbms1.sql, user_dbms2.sql")
    print("  - article_dbms1.sql, article_dbms2.sql")
    print("  - read_dbms1.sql, read_dbms2.sql")


if __name__ == "__main__":
    generate_partitioned_sql()
