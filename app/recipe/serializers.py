"""
Serializers for Recipe API
"""

from rest_framework import serializers

from core.models import Ingredient, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient object"""

    class Meta:
        model = Ingredient
        fields = ("id", "name")
        read_only_fields = ("id",)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe object"""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "time_minutes",
            "price",
            "link",
            "tags",
            "ingredients",
        )
        read_only_fields = ("id",)

    def _get_or_create_tags(self, tags_data, recipe):
        """Get or create tags for the recipe"""
        auth_user = self.context["request"].user
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag_data,
            )
            recipe.tags.add(tag)

    def _get_or_create_ingredients(self, ingredients_data, recipe):
        """Get or create ingredients for the recipe"""
        auth_user = self.context["request"].user
        for ingredient_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient_data,
            )
            recipe.ingredients.add(ingredient)

    def create(self, validated_data):
        """Create a recipe"""
        tags_data = validated_data.pop("tags", [])
        ingredients_data = validated_data.pop("ingredients", [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags_data, recipe)
        self._get_or_create_ingredients(ingredients_data, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe"""
        tags_data = validated_data.pop("tags", None)
        ingredients_data = validated_data.pop("ingredients", None)
        if tags_data is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags_data, instance)
        if ingredients_data is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients_data, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serialize a recipe detail"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ("description",)
