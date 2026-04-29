# from django.shortcuts import render
# from rest_framework.generics import ListAPIView, APIView
# from rest_framework.views APIView

# class CategoryTreeView(APIView):
#     def get(self, request):
#         if request.query

# class ProductAttributesCoordinator(APIView):
#     def get(self, request):
#         present_keys = request.query_params.keys()
#         response_data = {}

#         handlers = {
#             "categories": self.get_category_filters,
#             "brands": self.get_brand_filters,
#             "product_tags": self.get_tag_filters,
#             "product_attributies": self.get_attribute_filters,
#         }

#         for key, handler_func in handlers.items():
#             if key in present_keys:
#                 slugs = request.query_params.getlist(key)
#                 response_data[key] = handler_func(slugs)

#         def get_category_filters(self, slugs):
#             pass

#         def get_brand_filters(self, slugs):
#             pass

#         def get_tag_filters(self, slugs):
#             pass

#         def get_attribute_filters(self, slugs):
#             pass


class ProductOrdering(ListAPIView):
    pass
