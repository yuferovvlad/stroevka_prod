from django.db import models
from django.forms import ModelForm
# from django.shortcuts import reverse
from django.core.exceptions import ValidationError

# Create your models here.

SHIRT_SIZES = (
    ('1', 'Средний и старший НС'),
    ('2', 'Рядовой и младший НС'),
    ('3', 'Служащий'),
)
TOP_CATEGORY = (
    ('1', 'Считать как "В строю"'),
    ('2', 'Считать как "На удаленке"'),
    ('3', 'Считать как "В распоряжении"'),
    ('4', 'Считать как "Отсутствующие"'),
)
class UsersShtat(models.Model):
    name = models.CharField("наименование по штату", max_length=2, choices=SHIRT_SIZES)
    count_shtat = models.IntegerField("Всего по штату")

    def __str__(self):
        return f"{self.get_name_display()}"
        
    class Meta:
        verbose_name = "Кол-во по штату"
        verbose_name_plural = "Кол-во по штату сотрудников"


class TableStat(models.Model):
    name = models.CharField("Категория", max_length=150)
    parent = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE, related_name='children')
    icon = models.CharField(
        "Иконка fontawesome", blank=True, null=True, max_length=50)
    number = models.PositiveIntegerField(
        "Последовательность", default=1, unique=True, help_text="Указать номер категории по порядку")
    user_view = models.BooleanField("Показывать имена пользователей", default=True)
    check_top_category = models.CharField(
        "Как учитывать категорию?", max_length=1, blank=True, null=True, choices=TOP_CATEGORY)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('number', )
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class TableUsers(models.Model):
    name = models.CharField("Имя сотрудника", max_length=100)
    user_category = models.ForeignKey(
        UsersShtat, verbose_name="Категория сотрудника", on_delete=models.CASCADE, null=True)
    doljnost = models.TextField(
        "Должность сотрудника", blank=True)
    user_corona = models.BooleanField(
        "Проходил обследование на COVID-19?", default=False)
    user_vakcina_corona = models.BooleanField(
        "Проходил вакцинацию от СОVID-19?", default=False)
    user_status = models.ForeignKey(
        TableStat, verbose_name="Где находится", on_delete=models.CASCADE, null=True)
    user_date_range = models.CharField("Период отпуска / больничного / отпуска по личным обстоятельствам", max_length=19, blank=True, null=True)
    image = models.ImageField(
        verbose_name="Подпись", upload_to='images', blank=True)
    users_sign = models.BooleanField(
        verbose_name="Использовать подпись?", default=False)

    def save(self, *args, **kwargs):
        if self.users_sign:
            qs = TableUsers.objects.filter(users_sign=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() != 0:
                # choose ONE of the next two lines
                #self.users_sign = False  # keep the existing "chosen one"
                qs.update(users_sign=False) # make this obj "the chosen one"
        super(TableUsers, self).save(*args, **kwargs)

    # def get_update_url(self):
    #     return reverse('list_users_edit_url', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
        
    class Meta:
        ordering = ("name", )
        verbose_name = "Имя"
        verbose_name_plural = "Имена"
