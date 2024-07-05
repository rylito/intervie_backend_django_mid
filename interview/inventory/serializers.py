from rest_framework import serializers

from interview.inventory.models import Inventory, InventoryLanguage, InventoryTag, InventoryType


class InventoryTagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InventoryTag
        fields = ['id', 'name', 'is_active']
        
        
class InventoryLanguageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InventoryLanguage
        fields = ['id', 'name']


class InventoryTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InventoryType
        fields = ['id', 'name']


class InventorySerializer(serializers.ModelSerializer):
    type = InventoryTypeSerializer()
    language = InventoryLanguageSerializer()
    tags = InventoryTagSerializer(many=True)
    metadata = serializers.JSONField()
    
    class Meta:
        model = Inventory
        fields = ['id', 'name', 'type', 'language', 'tags', 'metadata']

    def create(self, validated_data):

        # pop the nested relation data from the validated_data
        inventory_type_data = validated_data.pop('type')
        language_data = validated_data.pop('language')
        tags_data = validated_data.pop('tags')

        # create these two related objects that Inventory references
        inventory_type_obj = InventoryType.objects.create(**inventory_type_data)
        language_obj = InventoryLanguage.objects.create(**language_data)

        # create the Inventory object now that the relations are created
        inventory_obj = Inventory.objects.create(
            type=inventory_type_obj,
            language=language_obj,
            **validated_data
        )

        # now create the m2m relations
        for tag_data in tags_data:
            inventory_obj.tags.create(**tag_data)

        return inventory_obj
