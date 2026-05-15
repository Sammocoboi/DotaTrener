'''
вся алгоритмическая логика работа с несколькими моделями расчеты валидация требующая доступ к бд

'''
from typing import List,Set
from django.db.models import Prefetch
from stratz_meta.models import StratzPatch,HeroBuild,HeroMeta

class StratzSelectionService:
    #сервис для подбора блюд по выбранной категории и набору продусктов
    """
    метод класса который не получает автоматически ссылку на экземпляр
    на экземпляр класс(self) и не получает ссылку на сам класс
    формально вдет себя как обынчая функция но логически приндлежти самому
    классу и вызывается через класс или его экземпляр
    """
    """
    возращаем список блюд заданной категроии
    для которых все ингредеинты содержатьсяв пределах product_id
    """
    """
    @staticmethod
    def get_possible_heroes(heroe:id,heroes_ids:List[int] -> List[HeroMeta]):
        heroes = HeroMeta.objects.filter(heroe=heroe).prefetch_related(
                Prefetch('HeroMeta',queryset=HeroMeta.objects.only('id'))
        )
        heroes_set = set(heroes_ids)
        result = []
        for her in heroes:
            heroe_meta_set=set(her.HeroBuild.value_list('id',flat=True))
            if heroe_meta_set.issubset(heroes_set):
                result.append(her)
        return result
    

    @staticmethod
    def get_product():
        s=0   
        """