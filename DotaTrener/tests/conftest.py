import pytest
from django.contrib.auth.models import User

from coaching.models import (
    Coach,
    Hero,
    Match,
    Mistake,
    MistakeCategory,
    Player,
    Review,
)
from stratz_meta.models import HeroBuild, HeroMeta, StratzPatch


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testplayer", password="testpass123")


@pytest.fixture
def coach_user(db):
    return User.objects.create_user(username="testcoach", password="testpass123")


@pytest.fixture
def player(user):
    return Player.objects.create(user=user, current_mmr=3500, peak_mmr=4000)


@pytest.fixture
def coach(coach_user):
    return Coach.objects.create(
        user=coach_user,
        specialization="Mid",
        bio="Coach bio",
        rating=4.5,
    )


@pytest.fixture
def hero(db):
    return Hero.objects.create(
        steam_id=1,
        name="npc_dota_hero_antimage",
        localized_name="Anti-Mage",
        primary_attr="agi",
        roles=["Carry"],
    )


@pytest.fixture
def patch(db):
    return StratzPatch.objects.create(version="7.40b", is_current=True)


@pytest.fixture
def hero_meta(hero, patch):
    return HeroMeta.objects.create(
        hero=hero,
        patch=patch,
        pick_rate=12.5,
        win_rate=51.2,
        ban_rate=3.0,
        games_played=10000,
        roles={"Carry": 95.0},
    )


@pytest.fixture
def match(player, hero):
    return Match.objects.create(
        player=player,
        match_id="1234567890",
        hero=hero,
        player_side="radiant",
        result="win",
        lobby_type="ranked",
        duration_seconds=2400,
        kills=10,
        deaths=2,
        assists=15,
        gpm=600,
        xpm=700,
    )


@pytest.fixture
def review(match, coach):
    return Review.objects.create(
        match=match,
        coach=coach,
        overall_score=7,
        summary="Solid game, improve map awareness.",
        status="completed",
    )


@pytest.fixture
def mistake_category(db):
    return MistakeCategory.objects.create(
        name="Positioning",
        description="Bad positioning in fights",
    )


@pytest.fixture
def mistake(review, mistake_category):
    return Mistake.objects.create(
        review=review,
        category=mistake_category,
        timestamp_seconds=1200,
        description="Died alone in enemy jungle",
        recommendation="Ward before farming",
        severity="high",
    )


@pytest.fixture
def hero_build(hero_meta):
    return HeroBuild.objects.create(
        hero_meta=hero_meta,
        build_type="item",
        sequence=[{"id": 1, "name": "Blink Dagger"}],
        pick_rate=5.0,
        win_rate=52.0,
        games=5000,
    )
