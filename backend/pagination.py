from rest_framework import pagination, serializers
from rest_framework.pagination import PageNumberPagination




class CustomPagination(pagination.LimitOffsetPagination):
    default_limit = 1000
    max_limit = 1000000
    min_limit = 1
    min_offset = 0
    max_offset = 1000000
    def paginate_queryset(self, queryset, request, view=None):
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')

        if limit:
            limit = int(limit)

            if limit > self.max_limit:
                raise serializers.ValidationError(
                    {"limit": ["Limit should be less than or equal to {0}".format(self.max_limit)]})

            elif limit < self.min_limit:
                raise serializers.ValidationError(
                    {"limit": ["Limit should be greater than or equal to {0}".format(self.min_limit)]})

            if offset:
                offset = int(offset)

                if offset > self.max_offset:
                    raise serializers.ValidationError(
                        {"offset": ["Offset should be less than or equal to {0}".format(self.max_offset)]})

            elif offset < self.min_offset:
                raise serializers.ValidationError(
                    {"offset": ["Offset should be greater than or equal to {0}".format(self.min_offset)]})

        return super(self.__class__, self).paginate_queryset(queryset, request,
                                                             view)




class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 5000
    def paginate_queryset(self, queryset, request, view=None):
        page_size = request.query_params.get('page_size')

        if page_size:
            if page_size.isdigit():
                limit = int(page_size)

                if limit > self.max_page_size:
                    error = {"statusCode": 400, "error": True, "data": "",
                             "message": "Bad Request, Please check request",
                             "errors": {"page_size": [
                                 "page_size should be less than or equal to {0}".format(self.max_page_size)], }}
                    raise serializers.ValidationError(error)
            else:
                error = {"statusCode": 400, "error": True, "data": "",
                         "message": "Bad Request, Please check request",
                         "errors": {"page_size": [
                             "Invalid page_size."]}}
                raise serializers.ValidationError(
                    error)

        return super(self.__class__, self).paginate_queryset(queryset, request,
                                                             view)