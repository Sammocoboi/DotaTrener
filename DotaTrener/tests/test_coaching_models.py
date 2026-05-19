import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

from coaching.models import (
    Coach,
    Hero,
    Match,
    Mistake,
    MistakeCategory,
    Player,
    Review,
)


@pytest.mark.django_db
class TestPlayer:
    def test_str(self, player):
        assert str(player) == "Player: testplayer (MMR: 3500)"

    def test_defaults(self, user):
        p = Player.objects.create(user=user)
        assert p.current_mmr == 0
        assert p.peak_mmr == 0
        assert p.favorite_role is None

    def test_cascade_on_user_delete(self, player, user):
        user_id = user.pk
        user.delete()
        assert not Player.objects.filter(pk=player.pk).exists()
        assert not User.objects.filter(pk=user_id).exists()


@pytest.mark.django_db
class TestCoach:
    def test_str(self, coach):
        assert str(coach) == "Coach: testcoach"

    def test_rating_in_range(self, coach_user):
        coach = Coach(user=coach_user, rating=5.0)
        coach.full_clean()

    def test_rating_out_of_range_raises(self, coach_user):
        coach = Coach(user=coach_user, rating=5.1)
        with pytest.raises(ValidationError):
            coach.full_clean()


@pytest.mark.django_db
class TestHero:
    def test_str(self, hero):
        assert str(hero) == "Anti-Mage"

    def test_unique_steam_id(self, hero):
        with pytest.raises(IntegrityError):
            Hero.objects.create(
                steam_id=hero.steam_id,
                name="duplicate",
                localized_name="Duplicate",
                primary_attr="str",
            )


@pytest.mark.django_db
class TestMatch:
    def test_str(self, match):
        assert "1234567890" in str(match)
        assert "Anti-Mage" in str(match)

    def test_unique_match_id(self, match, player, hero):
        with pytest.raises(IntegrityError):
            Match.objects.create(
                player=player,
                match_id=match.match_id,
                hero=hero,
                player_side="dire",
                result="loss",
                duration_seconds=1800,
            )

    def test_ordering_newest_first(self, player, hero):
        now = timezone.now()
        older = Match.objects.create(
            player=player,
            match_id="older",
            hero=hero,
            player_side="radiant",
            result="win",
            duration_seconds=1000,
            played_at=now - timedelta(days=1),
        )
        newer = Match.objects.create(
            player=player,
            match_id="newer",
            hero=hero,
            player_side="radiant",
            result="win",
            duration_seconds=2000,
            played_at=now,
        )
        ids = list(
            Match.objects.filter(player=player).values_list("match_id", flat=True)
        )
        assert ids[0] == newer.match_id

    def test_hero_set_null_on_delete(self, match, hero):
        hero_id = hero.pk
        hero.delete()
        match.refresh_from_db()
        assert match.hero_id is None

    def test_cascade_on_player_delete(self, match, player):
        player.delete()
        assert not Match.objects.filter(pk=match.pk).exists()


@pytest.mark.django_db
class TestMistakeCategory:
    def test_str(self, mistake_category):
        assert str(mistake_category) == "Positioning"

    def test_unique_name(self, mistake_category):
        with pytest.raises(IntegrityError):
            MistakeCategory.objects.create(name=mistake_category.name)


@pytest.mark.django_db
class TestReview:
    def test_str(self, review):
        assert "testcoach" in str(review)
        assert "1234567890" in str(review)

    def test_one_review_per_match(self, review, match, coach):
        with pytest.raises(IntegrityError):
            Review.objects.create(
                match=match,
                coach=coach,
                overall_score=5,
                summary="Duplicate",
            )

    def test_score_validation(self, match, coach):
        review = Review(
            match=match,
            coach=coach,
            overall_score=11,
            summary="Invalid",
        )
        with pytest.raises(ValidationError):
            review.full_clean()

    def test_cascade_on_match_delete(self, review, match):
        match.delete()
        assert not Review.objects.filter(pk=review.pk).exists()


@pytest.mark.django_db
class TestMistake:
    def test_str(self, mistake):
        assert "1200s" in str(mistake)
        assert "Positioning" in str(mistake)

    def test_str_without_category(self, review):
        m = Mistake.objects.create(
            review=review,
            timestamp_seconds=60,
            description="No category",
            recommendation="Fix it",
            severity="low",
        )
        assert "Без категории" in str(m)

    def test_ordering_by_timestamp(self, review):
        m2 = Mistake.objects.create(
            review=review,
            timestamp_seconds=2000,
            description="Late",
            recommendation="—",
            severity="medium",
        )
        m1 = Mistake.objects.create(
            review=review,
            timestamp_seconds=100,
            description="Early",
            recommendation="—",
            severity="low",
        )
        timestamps = list(
            Mistake.objects.filter(review=review).values_list(
                "timestamp_seconds", flat=True
            )
        )
        assert timestamps[0] == m1.timestamp_seconds
        assert timestamps[-1] == m2.timestamp_seconds

    def test_cascade_on_review_delete(self, mistake, review):
        review.delete()
        assert not Mistake.objects.filter(pk=mistake.pk).exists()
