from flask import Blueprint, render_template

from repositories import tag_repository

tags_bp = Blueprint("tags", __name__)


@tags_bp.route("/tags")
def tags_get() -> str:
    popular_tags = tag_repository.get_popular_tags()
    tag_counts = tag_repository.get_tag_counts()
    return render_template(
        "tags.html", popular_tags=popular_tags, tag_counts=tag_counts
    )
