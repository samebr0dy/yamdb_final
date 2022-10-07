# Generated by Django 2.2.16 on 2022-08-07 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_alter_categories_options_alter_comments_options_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Genres',
            new_name='Category',
        ),
        migrations.RenameModel(
            old_name='Comments',
            new_name='Comment',
        ),
        migrations.RenameModel(
            old_name='Categories',
            new_name='Genre',
        ),
        migrations.RenameModel(
            old_name='GenresTitles',
            new_name='GenreTitle',
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'verbose_name': 'Жанр', 'verbose_name_plural': 'Жанры'},
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'user'), ('moderator', 'moderator'), ('admin', 'admin')], default='user', max_length=9),
        ),
    ]
