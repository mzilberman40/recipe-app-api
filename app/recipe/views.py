"""
Views for recipe APIs
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core.models import Recipe, Tag, Ingredient
from recipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='tags',
                type=OpenApiTypes.STR,
                description='Comma separated List tag IDs to filter',
            ),
            OpenApiParameter(
                name='ingredients',
                type=OpenApiTypes.STR,
                description='Comma separated List ingredient IDs to filter',
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage Recipe APIs """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(param) for param in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        queryset = self.queryset
        tags = self.request.query_params.get('tags', None)
        ingredients = self.request.query_params.get('ingredients', None)
        if tags:
            tags_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)
        if ingredients:
            ingredients_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        return queryset.filter(user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload_image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='assigned_only',
                type=OpenApiTypes.INT, enum=[0,1],
                description='Filter by items assigned to recipes',
            ),
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                            mixins.ListModelMixin, viewsets.GenericViewSet):
    """View for manage recipe attrs APIs """
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        """Retrieve tags for authenticated user"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """View for manage TAGs APIs """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """View for manage Ingredients APIs """
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

