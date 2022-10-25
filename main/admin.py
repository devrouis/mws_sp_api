from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from main.models import *
import csv
from django.http import HttpResponse
from django.contrib import messages


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'last_name', 'first_name', 'password')}),
        (_('Personal info'), {
            'fields': ('seller_id', 'mws_auth_token', 'market_place')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'paid')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'last_name', 'first_name', 'seller_id', 'mws_auth_token', 'market_place', 'password1', 'password2', 'is_active', 'is_superuser', 'is_staff', 'paid'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    ordering = ('email',)
    list_display = ('email', 'last_name', 'first_name', 'seller_id', 'mws_auth_token',
                    'market_place', 'is_staff', 'is_active', 'is_superuser', 'paid')
    actions = ['export_as_csv', 'mark_as_paid', 'mark_as_unpaid']

    def export_as_csv(modeladmin, request, queryset):
        meta = User._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            meta)
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field)
                                  for field in field_names])
        return response

    def mark_as_paid(modeladmin, request, queryset):
        queryset.update(paid=True)
        messages.success(request, '課金ステータス更新が完了しました。')

    def mark_as_unpaid(modeladmin, request, queryset):
        queryset.update(paid=False)
        messages.success(request, '課金ステータス更新が完了しました。')

    mark_as_paid.short_description = '課金ステータス更新（課金）'
    mark_as_unpaid.short_description = '課金ステータス更新（非課金）'
    export_as_csv.short_description = "ユーザ情報ダウンロード"

    search_fields = ('first_name', 'last_name', 'email', )


class AppSettingsAdmin(admin.ModelAdmin):
    list_display = [
        field.name for field in AppSettings._meta.fields if field.name != "id"]


class ScrapeRequestAdmin(admin.ModelAdmin):
    list_display = [
        field.name for field in ScrapeRequest._meta.fields if field.name != "id"]


class ScrapeResultAdmin(admin.ModelAdmin):
    list_display = [
        field.name for field in ScrapeRequestResult._meta.fields if field.name != "id"]


class PaypalSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        field.name for field in PaypalSubscription._meta.fields if field.name != "id"]


admin.site.site_title = '管理'
admin.site.site_header = 'ams admin '
admin.site.index_title = 'Menu'
admin.site.register(User, MyUserAdmin)
admin.site.register(AppSettings, AppSettingsAdmin)
admin.site.register(ScrapeRequest, ScrapeRequestAdmin)
admin.site.register(ScrapeRequestResult, ScrapeResultAdmin)
admin.site.register(PaypalSubscription, PaypalSubscriptionAdmin)
