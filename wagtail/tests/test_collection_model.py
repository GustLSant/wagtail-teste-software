from django.test import TestCase
from wagtail.models import Collection, GroupCollectionPermission
from django.contrib.auth.models import Group, Permission





class TestCollectionTreeOperations(TestCase):
    def setUp(self):
        self.root_collection = Collection.get_first_root_node()
        self.holiday_photos_collection = self.root_collection.add_child(
            name="Holiday photos"
        )
        self.evil_plans_collection = self.root_collection.add_child(name="Evil plans")
        # self.holiday_photos_collection's path has been updated out from under it by the addition of a sibling with
        # an alphabetically earlier name (due to Collection.node_order_by = ['name']), so we need to refresh it from
        # the DB to get the new path.
        self.holiday_photos_collection.refresh_from_db()

    def test_alphabetic_sorting(self):
        old_evil_path = self.evil_plans_collection.path
        old_holiday_path = self.holiday_photos_collection.path
        # Add a child to Root that has an earlier name than "Evil plans" and "Holiday Photos".
        alpha_collection = self.root_collection.add_child(name="Alpha")
        # Take note that self.evil_plans_collection and self.holiday_photos_collection have not yet changed.
        self.assertEqual(old_evil_path, self.evil_plans_collection.path)
        self.assertEqual(old_holiday_path, self.holiday_photos_collection.path)
        # Update the two Collections from the database.
        self.evil_plans_collection.refresh_from_db()
        self.holiday_photos_collection.refresh_from_db()
        # Confirm that the "Evil plans" and "Holiday photos" paths have changed in the DB due to adding "Alpha".
        self.assertNotEqual(old_evil_path, self.evil_plans_collection.path)
        self.assertNotEqual(old_holiday_path, self.holiday_photos_collection.path)
        # Confirm that Alpha is before Evil Plans and Holiday Photos, due to Collection.node_order_by = ['name'].
        self.assertLess(alpha_collection.path, self.evil_plans_collection.path)
        self.assertLess(alpha_collection.path, self.holiday_photos_collection.path)

    def test_get_ancestors(self):
        self.assertEqual(
            list(self.holiday_photos_collection.get_ancestors().order_by("path")),
            [self.root_collection],
        )
        self.assertEqual(
            list(
                self.holiday_photos_collection.get_ancestors(inclusive=True).order_by(
                    "path"
                )
            ),
            [self.root_collection, self.holiday_photos_collection],
        )

    def test_get_descendants(self):
        self.assertEqual(
            list(self.root_collection.get_descendants().order_by("path")),
            [self.evil_plans_collection, self.holiday_photos_collection],
        )
        self.assertEqual(
            list(self.root_collection.get_descendants(inclusive=True).order_by("path")),
            [
                self.root_collection,
                self.evil_plans_collection,
                self.holiday_photos_collection,
            ],
        )

    def test_get_siblings(self):
        self.assertEqual(
            list(self.holiday_photos_collection.get_siblings().order_by("path")),
            [self.evil_plans_collection, self.holiday_photos_collection],
        )
        self.assertEqual(
            list(
                self.holiday_photos_collection.get_siblings(inclusive=False).order_by(
                    "path"
                )
            ),
            [self.evil_plans_collection],
        )

    def test_get_next_siblings(self):
        self.assertEqual(
            list(self.evil_plans_collection.get_next_siblings().order_by("path")),
            [self.holiday_photos_collection],
        )
        self.assertEqual(
            list(
                self.holiday_photos_collection.get_next_siblings(
                    inclusive=True
                ).order_by("path")
            ),
            [self.holiday_photos_collection],
        )
        self.assertEqual(
            list(self.holiday_photos_collection.get_next_siblings().order_by("path")),
            [],
        )

    def test_get_prev_siblings(self):
        self.assertEqual(
            list(self.holiday_photos_collection.get_prev_siblings().order_by("path")),
            [self.evil_plans_collection],
        )
        self.assertEqual(
            list(self.evil_plans_collection.get_prev_siblings().order_by("path")), []
        )
        self.assertEqual(
            list(
                self.evil_plans_collection.get_prev_siblings(inclusive=True).order_by(
                    "path"
                )
            ),
            [self.evil_plans_collection],
        )


##################################################################




class TestCollection(TestCase):
    def setUp(self):
        self.root_collection = Collection.get_first_root_node()
        self.holiday_photos_collection = self.root_collection.add_child(name="Holiday photos")
        self.evil_plans_collection = self.root_collection.add_child(name="Evil plans")

    def test_get_indented_name(self):
        indented_name = self.holiday_photos_collection.get_indented_name()
        self.assertEqual(indented_name, "Holiday photos")  # Verifica se o nome é exibido corretamente sem indentação

    def test_get_view_restrictions(self):
        view_restrictions = self.holiday_photos_collection.get_view_restrictions()
        self.assertEqual(view_restrictions.count(), 0)  # Verifica se não há restrições de visualização associadas à coleção

    def test_get_indented_choices(self):
        choices = Collection.objects.get_indented_choices()
        self.assertEqual(len(choices), 3)  # Verifica se há 3 escolhas (raiz, fotos de férias, planos malignos) disponíveis

    def test_collection_member_creation(self):
        class TestCollectionMember(CollectionMember):
            pass

        collection_member = TestCollectionMember.objects.create(collection=self.holiday_photos_collection)
        self.assertEqual(TestCollectionMember.objects.count(), 1)  # Verifica se existe um membro de coleção criado
        self.assertEqual(collection_member.collection, self.holiday_photos_collection)  # Verifica se a coleção associada está correta

    def test_group_collection_permission_deletion(self):
        group = Group.objects.create(name="Test Group")
        permission = Permission.objects.create(name="Test Permission", codename="test_permission")
        group_collection_permission = GroupCollectionPermission.objects.create(
            group=group,
            collection=self.holiday_photos_collection,
            permission=permission
        )
        group_collection_permission.delete()
        self.assertEqual(GroupCollectionPermission.objects.count(), 0)  # Verifica se a permissão de grupo foi excluída

    def test_collection_member_search_fields(self):
        class TestCollectionMember(CollectionMember):
            pass

        collection_member = TestCollectionMember.objects.create(collection=self.holiday_photos_collection)
        results = TestCollectionMember.objects.filter(collection=self.holiday_photos_collection)
        self.assertEqual(results.count(), 1)  # Verifica se o membro da coleção é retornado corretamente nos resultados de pesquisa

    def test_get_root_collection_id(self):
        root_collection_id = get_root_collection_id()
        self.assertEqual(root_collection_id, self.root_collection.id)  # Verifica se o ID da coleção raiz é retornado corretamente

    def test_group_collection_permission_natural_key(self):
        group = Group.objects.create(name="Test Group")
        permission = Permission.objects.create(name="Test Permission", codename="test_permission")
        group_collection_permission = GroupCollectionPermission.objects.create(
            group=group,
            collection=self.holiday_photos_collection,
            permission=permission
        )
        natural_key = group_collection_permission.natural_key()
        expected_key = (group, self.holiday_photos_collection, permission)
        self.assertEqual(natural_key, expected_key)  # Verifica se a chave natural é gerada corretamente

    def test_collection_query_set_ordering(self):
        collection_query_set = Collection.objects.all()
        ordered_collections = collection_query_set.order_by("name")
        self.assertEqual(list(ordered_collections), [self.evil_plans_collection, self.holiday_photos_collection, self.root_collection])
        # Verifica se as coleções estão ordenadas alfabeticamente pelo nome
