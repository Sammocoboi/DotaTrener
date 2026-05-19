import pytest
from django.db import IntegrityError

from coaching.models import Hero
from stratz_meta.models import HeroBuild, HeroMeta, StratzPatch


@pytest.mark.django_db
class TestStratzPatch:
    def test_str(self, patch):
        assert str(patch) == "Patch 7.40b"

    def test_version_is_primary_key(self, patch):
        assert patch.pk == "7.40b"

    def test_unique_version(self, patch):
        with pytest.raises(IntegrityError):
            StratzPatch.objects.create(version=patch.version)


@pytest.mark.django_db
class TestHeroMeta:
    def test_unique_hero_per_patch(self, hero_meta, hero, patch):
        with pytest.raises(IntegrityError):
            HeroMeta.objects.create(hero=hero, patch=patch)

    def test_related_name_builds(self, hero_meta, hero_build):
        assert hero_meta.builds.count() == 1
        assert hero_meta.builds.first() == hero_build

    def test_related_name_stratz_meta_on_hero(self, hero_meta, hero):
        assert hero.stratz_meta.count() == 1

    def test_cascade_on_hero_delete(self, hero_meta, hero):
        hero.delete()
        assert not HeroMeta.objects.filter(pk=hero_meta.pk).exists()

    def test_cascade_on_patch_delete(self, hero_meta, patch):
        patch.delete()
        assert not HeroMeta.objects.filter(pk=hero_meta.pk).exists()

    def test_defaults(self, hero, patch):
        meta = HeroMeta.objects.create(hero=hero, patch=patch)
        assert meta.pick_rate == 0.0
        assert meta.win_rate == 0.0
        assert meta.ban_rate == 0.0
        assert meta.games_played == 0
        assert meta.roles == {}


@pytest.mark.django_db
class TestHeroBuild:
    def test_create_item_build(self, hero_build):
        assert hero_build.build_type == "item"
        assert hero_build.sequence[0]["name"] == "Blink Dagger"
        assert hero_build.games == 5000

    def test_create_skill_build(self, hero_meta):
        build = HeroBuild.objects.create(
            hero_meta=hero_meta,
            build_type="skill",
            sequence=[
                {"id": 5003, "name": "Mana Break L1"},
                {"id": 5004, "name": "Blink L2"},
            ],
            win_rate=48.5,
            games=25000,
        )
        assert build.build_type == "skill"
        assert len(build.sequence) == 2

    def test_cascade_on_hero_meta_delete(self, hero_build, hero_meta):
        hero_meta.delete()
        assert not HeroBuild.objects.filter(pk=hero_build.pk).exists()

    def test_multiple_builds_per_hero_meta(self, hero_meta):
        HeroBuild.objects.create(
            hero_meta=hero_meta,
            build_type="item",
            sequence=[{"id": 1, "name": "Item A"}],
        )
        HeroBuild.objects.create(
            hero_meta=hero_meta,
            build_type="skill",
            sequence=[{"id": 2, "name": "Skill A"}],
        )
        assert hero_meta.builds.count() == 2
