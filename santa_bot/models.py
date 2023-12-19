from django.db import models


class Organizer(models.Model):
    telegram_id = models.IntegerField(unique=True,
                                      verbose_name='ID в телеграмме')

    def __str__(self):
        return f'@{self.telegram_id}'

    class Meta:
        verbose_name = 'Организатор'
        verbose_name_plural = 'Организаторы'


class Game(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Название')

    description = models.TextField(null=True,
                                   blank=True,
                                   verbose_name='Описание')

    organizer = models.ForeignKey(Organizer,
                                  on_delete=models.CASCADE,
                                  null=True,
                                  blank=True,
                                  verbose_name='Организатор',
                                  related_name='organizer')

    price_limit = models.CharField(verbose_name='Стоимость',
                                   max_length=200)

    start_date = models.DateField(null=True,
                                  blank=True,
                                  verbose_name='Дата начала',
                                  auto_now_add=True)

    end_date = models.DateField(null=True,
                                blank=True,
                                verbose_name='Дата окончания')

    send_date = models.DateTimeField(null=True,
                                     blank=True,
                                     verbose_name='Дата отправки подарков')

    link = models.CharField(max_length=200,
                            null=True,
                            blank=True,
                            verbose_name='Ссылка на розыгрыш')

    players_distributed = models.BooleanField(verbose_name='Распределено?',
                                              default=False)

    def __str__(self):
        return f'@{self.name}'

    class Meta:
        verbose_name = 'Розыгрыш'
        verbose_name_plural = 'Розыгрыши'


class Player(models.Model):
    telegram_id = models.IntegerField(verbose_name='telegram ID')

    game = models.ForeignKey(Game,
                             verbose_name='Розыгрыш',
                             on_delete=models.CASCADE,
                             related_name='players')

    name = models.CharField(verbose_name='Имя',
                            max_length=50)

    # TODO: validate data and change CharField to EmailField
    email = models.CharField(verbose_name='Email',
                             max_length=254)

    wishlist = models.TextField(null=True,
                                blank=True,
                                verbose_name='Подарки')

    avoided_players = models.ManyToManyField('self',
                                             verbose_name='Избегаемые игроки',
                                             blank=True)

    giftee = models.ForeignKey('self',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               verbose_name='Кому дарит',
                               related_name='santa')

    wishlist_url = models.CharField(verbose_name='Ссылка на вишлист',
                                    max_length=300,
                                    blank=True,
                                    null=True,
                                    default=None)

    def __str__(self) -> str:
        return str(self.telegram_id)

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        unique_together = ['telegram_id', 'game']


class Image(models.Model):
    name = models.CharField(verbose_name='Название картинки',
                            max_length=250)
    file = models.ImageField(upload_to='')

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'
