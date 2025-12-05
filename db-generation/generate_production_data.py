#!/usr/bin/env python3
"""Generate production dataset with real BBC news texts, images, and videos.

This script generates partitioned SQL files for a distributed database system
with horizontal fragmentation. It uses real media files and applies proper
data distribution across DBMS1 and DBMS2.
"""

import os
import random
from pathlib import Path
from shutil import copyfile

import click


# Scale configurations
SCALES = {
    "10G": {"users": 10000, "articles": 10000, "reads": 1000000},
    "50G": {"users": 50000, "articles": 50000, "reads": 5000000},
    "100G": {"users": 100000, "articles": 100000, "reads": 10000000},
}

# Data distribution probabilities
REGION_BEIJING_PROB = 0.4  # 60% Beijing, 40% Hong Kong
CATEGORY_SCIENCE_PROB = 0.55  # 45% science, 55% technology
LANGUAGE_EN_PROB = 0.8  # 20% English, 80% Chinese
VIDEO_PROB = 0.05  # 5% of articles have video

# Read behavior probabilities [read, agree, comment, share]
READ_PROBS = {
    "Beijing+en": [0.6, 0.2, 0.2, 0.1],
    "Beijing+zh": [1.0, 0.3, 0.3, 0.2],
    "Hong Kong+en": [1.0, 0.3, 0.3, 0.2],
    "Hong Kong+zh": [0.8, 0.2, 0.2, 0.1],
}

# Global tracking dictionaries
uid_region = {}
aid_category = {}
bbc_categories = ["business", "entertainment", "sport", "tech"]
bbc_files_cache = {}


def load_bbc_files():
    """Load BBC news file lists once."""
    base_path = Path(__file__).parent / "bbc_news_texts"
    for category in bbc_categories:
        category_path = base_path / category
        if category_path.exists():
            bbc_files_cache[category] = sorted(os.listdir(category_path))
        else:
            click.echo(f"⚠ Warning: BBC category '{category}' not found")
            bbc_files_cache[category] = []


def get_random_bbc_text():
    """Get random BBC news text file path."""
    category = random.choice(bbc_categories)
    if not bbc_files_cache.get(category):
        return None
    filename = random.choice(bbc_files_cache[category])
    return Path(__file__).parent / "bbc_news_texts" / category / filename


def gen_user_values(i):
    """Generate user record values."""
    time_begin = 1506328859000
    user_id = f"u{i}"
    uid = str(i)
    name = f"user{i}"
    gender = "male" if random.random() > 0.33 else "female"
    email = f"email{i}"
    phone = f"phone{i}"
    dept = f"dept{int(random.random() * 20)}"
    grade = f"grade{int(random.random() * 4 + 1)}"
    language = "en" if random.random() > LANGUAGE_EN_PROB else "zh"
    region = "Beijing" if random.random() > REGION_BEIJING_PROB else "Hong Kong"
    role = f"role{int(random.random() * 3)}"
    prefer_tags = f"tags{int(random.random() * 50)}"
    obtained_credits = str(int(random.random() * 100))

    uid_region[uid] = region

    return (
        f"('{time_begin + i}', '{user_id}', '{uid}', '{name}', '{gender}', "
        f"'{email}', '{phone}', '{dept}', '{grade}', '{language}', "
        f"'{region}', '{role}', '{prefer_tags}', '{obtained_credits}')"
    )


def gen_article_values(i, articles_dir):
    """Generate article record values and copy real media files."""
    time_begin = 1506000000000
    article_id = f"a{i}"
    aid = str(i)
    title = f"title{i}"
    category = "science" if random.random() > CATEGORY_SCIENCE_PROB else "technology"
    abstract = f"abstract of article {i}"
    article_tags = f"tags{int(random.random() * 50)}"
    authors = f"author{int(random.random() * 2000)}"
    language = "en" if random.random() > 0.5 else "zh"

    aid_category[aid] = category

    # Create article directory
    article_path = articles_dir / f"article{i}"
    article_path.mkdir(parents=True, exist_ok=True)

    # Copy BBC news text
    text_filename = f"text_a{i}.txt"
    text_source = get_random_bbc_text()
    if text_source and text_source.exists():
        copyfile(text_source, article_path / text_filename)
    else:
        # Fallback: create simple text file
        (article_path / text_filename).write_text(
            f"Article {i} content.\nThis is a news article about {category}.\n"
        )

    # Copy random images (1-3 images per article)
    image_num = random.randint(1, 3)
    image_str = ""
    image_base_path = Path(__file__).parent / "image"

    for j in range(image_num):
        image_filename = f"image_a{i}_{j}.jpg"
        image_str += f"articles/article{i}/{image_filename},"

        # Copy random image from pool
        source_image = image_base_path / f"{random.randint(0, 599)}.jpg"
        if source_image.exists():
            copyfile(source_image, article_path / image_filename)
        else:
            # Create placeholder image
            (article_path / image_filename).write_bytes(
                b"\xff\xd8\xff\xe0" + b"\x00" * 1020
            )

    # Copy video (5% probability)
    video_str = ""
    if random.random() < VIDEO_PROB:
        video_filename = f"video_a{i}_video.flv"
        video_str = f"articles/article{i}/{video_filename}"

        video_base_path = Path(__file__).parent / "video"
        source_video = video_base_path / random.choice(["video1.flv", "video2.flv"])

        if source_video.exists():
            copyfile(source_video, article_path / video_filename)
        else:
            # Create placeholder video
            (article_path / video_filename).write_bytes(b"FLV\x01" + b"\x00" * 1020)

    # Store relative paths for database
    text_path = f"articles/article{i}/{text_filename}"

    return (
        f"('{time_begin + i}', '{article_id}', '{aid}', '{title}', '{category}', "
        f"'{abstract}', '{article_tags}', '{authors}', '{language}', "
        f"'{text_path}', '{image_str}', '{video_str}')"
    )


def gen_read_values(i, users_num, articles_num):
    """Generate read record values."""
    time_begin = 1506332297000
    read_id = f"r{i}"

    # Randomly select user and article
    uid = str(random.randint(0, users_num - 1))
    aid = str(random.randint(0, articles_num - 1))

    # Get user region and article language for probability calculation
    region = uid_region.get(uid, "Beijing")

    read_time_length = str(int(random.random() * 100))

    # Use region-based probabilities
    lang = "en" if random.random() > LANGUAGE_EN_PROB else "zh"
    prob_key = f"{region}+{lang}"
    probs = READ_PROBS.get(prob_key, READ_PROBS["Beijing+zh"])

    agree_or_not = "1" if random.random() < probs[1] else "0"
    comment_or_not = "1" if random.random() < probs[2] else "0"
    share_or_not = "1" if random.random() < probs[3] else "0"
    comment_detail = f"comment {i} on article {aid}"

    return (
        f"('{time_begin + i * 10000}', '{read_id}', '{uid}', '{aid}', "
        f"'{read_time_length}', '{agree_or_not}', '{comment_or_not}', '{share_or_not}', "
        f"'{comment_detail}')"
    )


@click.command()
@click.option(
    "--scale",
    type=click.Choice(["10G", "50G", "100G"]),
    default="10G",
    help="Dataset scale to generate",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default="generated_data",
    help="Output directory for SQL files",
)
@click.option(
    "--articles-dir",
    type=click.Path(path_type=Path),
    default="production_articles",
    help="Output directory for article media files",
)
def main(scale, output_dir, articles_dir):
    """Generate production dataset with real media files."""
    config = SCALES[scale]
    users_num = config["users"]
    articles_num = config["articles"]
    reads_num = config["reads"]

    click.echo(f"Generating production data ({scale} scale)...\n")
    click.echo(f"  Users: {users_num:,}")
    click.echo(f"  Articles: {articles_num:,}")
    click.echo(f"  Reads: {reads_num:,}\n")

    # Create output directories
    output_dir.mkdir(exist_ok=True)
    articles_dir.mkdir(exist_ok=True)

    # Load BBC news files
    click.echo("Loading BBC news texts...")
    load_bbc_files()
    total_bbc = sum(len(files) for files in bbc_files_cache.values())
    click.echo(f"  ✓ Found {total_bbc} BBC news articles\n")

    # Generate users
    click.echo(f"[1/4] Generating {users_num:,} users...")
    beijing_users = []
    hongkong_users = []

    for i in range(users_num):
        values = gen_user_values(i)
        region = uid_region[str(i)]

        if region == "Beijing":
            beijing_users.append(values)
        else:
            hongkong_users.append(values)

        if (i + 1) % 10000 == 0:
            click.echo(f"  Progress: {i + 1:,}/{users_num:,}")

    click.echo(f"  ✓ Beijing: {len(beijing_users):,} users")
    click.echo(f"  ✓ Hong Kong: {len(hongkong_users):,} users\n")

    # Write user SQL files
    with open(output_dir / "user_dbms1.sql", "w") as f:
        f.write("-- Users for DBMS1 (Beijing)\n")
        if beijing_users:
            f.write(
                'INSERT INTO "user" (timestamp, id, uid, name, gender, email, phone, '
                "dept, grade, language, region, role, preferTags, obtainedCredits) VALUES\n"
            )
            f.write(",\n".join(beijing_users))
            f.write(";\n")

    with open(output_dir / "user_dbms2.sql", "w") as f:
        f.write("-- Users for DBMS2 (Hong Kong)\n")
        if hongkong_users:
            f.write(
                'INSERT INTO "user" (timestamp, id, uid, name, gender, email, phone, '
                "dept, grade, language, region, role, preferTags, obtainedCredits) VALUES\n"
            )
            f.write(",\n".join(hongkong_users))
            f.write(";\n")

    # Generate articles with real media
    click.echo(f"[2/4] Generating {articles_num:,} articles with real media...")
    science_articles = []
    tech_articles = []
    video_count = 0

    for i in range(articles_num):
        values = gen_article_values(i, articles_dir)
        category = aid_category[str(i)]

        if category == "science":
            science_articles.append(values)
        else:
            tech_articles.append(values)

        # Count videos
        if f"video_a{i}_video.flv" in values:
            video_count += 1

        if (i + 1) % 5000 == 0:
            click.echo(f"  Progress: {i + 1:,}/{articles_num:,}")

    click.echo(f"  ✓ Science: {len(science_articles):,} articles (replicated to DBMS1)")
    click.echo(f"  ✓ Technology: {len(tech_articles):,} articles (DBMS2 only)")
    click.echo(
        f"  ✓ Articles with videos: {video_count:,} ({video_count / articles_num * 100:.1f}%)\n"
    )

    # Write article SQL files
    with open(output_dir / "article_dbms1.sql", "w") as f:
        f.write("-- Articles for DBMS1 (science only, replicated)\n")
        if science_articles:
            f.write(
                'INSERT INTO "article" (timestamp, id, aid, title, category, abstract, '
                "articleTags, authors, language, text, image, video) VALUES\n"
            )
            f.write(",\n".join(science_articles))
            f.write(";\n")

    with open(output_dir / "article_dbms2.sql", "w") as f:
        f.write("-- Articles for DBMS2 (science + technology)\n")
        all_articles = science_articles + tech_articles
        if all_articles:
            f.write(
                'INSERT INTO "article" (timestamp, id, aid, title, category, abstract, '
                "articleTags, authors, language, text, image, video) VALUES\n"
            )
            f.write(",\n".join(all_articles))
            f.write(";\n")

    # Count media files
    click.echo("[3/4] Media files summary...")
    total_images = sum(
        len(list((articles_dir / f"article{i}").glob("image_*.jpg")))
        for i in range(articles_num)
        if (articles_dir / f"article{i}").exists()
    )
    click.echo(f"  ✓ Copied {articles_num:,} BBC news texts")
    click.echo(f"  ✓ Copied {total_images:,} images")
    click.echo(f"  ✓ Copied {video_count:,} videos\n")

    # Generate reads
    click.echo(f"[4/4] Generating {reads_num:,} reads...")
    beijing_reads = []
    hongkong_reads = []

    for i in range(reads_num):
        values = gen_read_values(i, users_num, articles_num)

        # Extract uid to determine region
        # Parse uid from values string: "('timestamp', 'read_id', 'uid', ..."
        uid_start = values.find("', '", values.find("', '") + 1) + 4
        uid_end = values.find("'", uid_start)
        uid = values[uid_start:uid_end]

        region = uid_region.get(uid, "Beijing")

        if region == "Beijing":
            beijing_reads.append(values)
        else:
            hongkong_reads.append(values)

        if (i + 1) % 100000 == 0:
            click.echo(f"  Progress: {i + 1:,}/{reads_num:,}")

    click.echo(f"  ✓ Beijing users: {len(beijing_reads):,} reads")
    click.echo(f"  ✓ Hong Kong users: {len(hongkong_reads):,} reads\n")

    # Write read SQL files
    with open(output_dir / "read_dbms1.sql", "w") as f:
        f.write("-- Reads for DBMS1 (Beijing users)\n")
        if beijing_reads:
            f.write(
                'INSERT INTO "user_read" (timestamp, id, uid, aid, readTimeLength, '
                "agreeOrNot, commentOrNot, shareOrNot, commentDetail) VALUES\n"
            )
            f.write(",\n".join(beijing_reads))
            f.write(";\n")

    with open(output_dir / "read_dbms2.sql", "w") as f:
        f.write("-- Reads for DBMS2 (Hong Kong users)\n")
        if hongkong_reads:
            f.write(
                'INSERT INTO "user_read" (timestamp, id, uid, aid, readTimeLength, '
                "agreeOrNot, commentOrNot, shareOrNot, commentDetail) VALUES\n"
            )
            f.write(",\n".join(hongkong_reads))
            f.write(";\n")

    # Summary
    click.echo("✓ Data generation complete!\n")
    click.echo("Generated SQL files:")
    click.echo(f"  {output_dir}/user_dbms1.sql")
    click.echo(f"  {output_dir}/user_dbms2.sql")
    click.echo(f"  {output_dir}/article_dbms1.sql")
    click.echo(f"  {output_dir}/article_dbms2.sql")
    click.echo(f"  {output_dir}/read_dbms1.sql")
    click.echo(f"  {output_dir}/read_dbms2.sql")
    click.echo("\nGenerated article directories:")
    click.echo(f"  {articles_dir}/ ({articles_num:,} directories)")
    click.echo("\nNext steps:")
    click.echo(
        f"  1. Load data: uv run python src/cli/load_data.py bulk-load --sql-dir {output_dir}"
    )
    click.echo(
        f"  2. Upload media: uv run python src/cli/load_data.py upload-media --mock-dir {articles_dir}"
    )
    click.echo("  3. Populate aggregates: uv run python src/cli/populate_beread.py")


if __name__ == "__main__":
    main()
