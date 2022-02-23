from itertools import islice

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()

NUM_OF_OBJ = 10


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Sophia')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            author=cls.user,
            group=cls.group
        )
        cls.group_check = Group.objects.create(
            title='Проверочная группа',
            slug='checkslug',
            description='Проверочное описание'
        )

    def setUp(self):
        # Создаём авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'}
            ),
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем, соотвесоответствует ли ожиданиям словарь context,
    # передаваемый в шаблон при вызове
    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        test_object = response.context['page_obj'][0]
        self.assertEqual(test_object, self.post)

    def test_group_list_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        test_object = response.context['page_obj'][0]
        test_title = test_object.group.title
        test_author = test_object.author
        test_text = test_object.text
        test_group = test_object.group
        test_description = test_object.group.description
        self.assertEqual(test_object, self.post)
        self.assertEqual(test_title, 'Тестовая группа')
        self.assertEqual(test_author, self.user)
        self.assertEqual(test_text, 'Тестовый заголовок')
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_description, 'Тестовое описание')

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        test_object = response.context['page_obj'][0]
        test_title = test_object.group.title
        test_group = test_object.group
        test_description = test_object.group.description
        test_sum_of_posts = test_object.author.posts.all().count()
        self.assertEqual(test_object, self.post)
        self.assertEqual(test_title, 'Тестовая группа')
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_description, 'Тестовое описание')
        self.assertEqual(test_sum_of_posts, len(self.user.posts.all()))

    def test_post_detail_show_correct_context(self):
        response = self.client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': 1})
        )
        test_title = response.context.get('post').text
        test_group = response.context.get('post').group.title
        test_author = response.context.get('post').author
        test_sum_of_posts = response.context.get(
            'post').author.posts.all().count()
        self.assertEqual(test_title, self.post.text)
        self.assertEqual(test_group, 'Тестовая группа')
        self.assertEqual(test_author, self.user,)
        self.assertEqual(test_sum_of_posts, len(self.user.posts.all()))

    def test_create_post_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # Тест страницы редактирования поста
    def test_post_edit_page_show_correct_context(self):
        response = (self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        )
        self.assertIsInstance(response.context.get('form'), PostForm)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit = response.context['is_edit']
        self.assertTrue(is_edit)
        self.assertIsInstance(is_edit, bool)

    def test_post_appears_in_3_pages(self):
        """
        Проверяем, что при создании поста с группой, этот пост появляется:
        на главной странице сайта, на странице выбранной группы,
        в профайле пользователя. """
        # Проверяем, что первый элемент списка на главной странице сайта -
        # это созданный нами пост:
        response = self.authorized_client.get(reverse('posts:index'))
        object_on_main_site = response.context['page_obj'][0]
        self.assertEqual(object_on_main_site, self.post)
        # Проверяем, что первый элемент списка на странице группы -
        # это созданный нами пост:
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        test_object = response.context['page_obj'][0]
        test_group = test_object.group
        self_post = self.post
        self_group = self.group

        # Проверяем, что первый элемент списка в профайле пользователя -
        # это созданный нами пост:
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Sophia'})
        )
        test_sophia = response.context['page_obj'][0]
        self.assertEqual(test_object, self.post)

        # Создаем словарь с элементами страницы(ключ)
        # и ожидаемым контекстом (значение):
        context_matching = {
            test_object: self_post,
            test_group: self_group,
            test_sophia: self.post
        }
        for element, names in context_matching.items():
            with self.subTest(element=element):
                self.assertEqual(element, names)

    def test_post_not_found(self):
        """ Проверяем, что пост не попал на странице группы,
        для которой он не был предназначен """
        # Проверяем контекст:
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group_check.slug}
            )
        )
        context = response.context['page_obj'].object_list
        self.assertFalse(self.post in context)
        # Не удалось разобраться с assertIn

class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Sophia')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        batch_size = 13
        posts = (Post(
            text='Пост № %s' % i,
            author=cls.user,
            group=cls.group) for i in range(batch_size)
        )
        Post.objects.bulk_create(posts)

    def setUp(self):
        # Создаем авторизованный клиент:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_six_pages_contains_records(self):
        """
        Проверяем количество выводимых постов на странице
        """
        index_page = reverse('posts:index')
        grouplist_page = reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'})
        profile_page = reverse(
            'posts:profile', kwargs={'username': 'Sophia'})
        posts_on_page = {
            (index_page, 1): NUM_OF_OBJ,
            (grouplist_page, 1): NUM_OF_OBJ,
            (profile_page, 1): NUM_OF_OBJ,
            (index_page, 2): 3,
            (grouplist_page, 2): 3,
            (profile_page, 2): 3,
        }
        for (url, page), pages in posts_on_page.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url, {'page': page})
                self.assertEqual(len(response.context['page_obj']), pages)
