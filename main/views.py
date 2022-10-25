from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView
)
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView
from .forms import SignupForm, UserUpdateForm, RequestTextForm, RequestCsvForm, PasswordChangeForm, SettingUpdateForm
from .models import *
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import csv
from django.conf import settings
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.template.loader import get_template
from main.paypal_apis import get_client, create_subscription, cancel_subscription, list_billing_plans, update_subscription
import os
import datetime
import logging

import subprocess
import shlex
import json


def process_tasks():
    process_tasks_cmd = "python manage.py process_tasks &"
    process_tasks_args = shlex.split(process_tasks_cmd)
    process_tasks_subprocess = subprocess.Popen(process_tasks_args)


# emp=Employee.objects.get(EmployeeId=request.data.get("Emp"))
# process_tasks()


# Create your views here.
class Login(LoginView):
    """ログインページ"""
    template_name = 'login.html'


class Logout(LogoutView):
    pass


class Signup(CreateView):
    form_class = SignupForm
    template_name = "signup.html"
    success_url = reverse_lazy('top')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        # domain = current_site.domain
        # baseurl = f'{self.request.scheme}://{domain}'
        appsettings = AppSettings.load()
        baseurl = f'http://{appsettings.server_hostname}' if settings.DJANGO_ENV == 'prod' else 'http://localhost:8000'
        context = {
            'user': user,
            'baseurl': baseurl,
            'token': dumps(user.pk),
        }
        subject = 'ユーザ登録'
        # message = get_template('mail/signup.txt').render(context)
        # try:
        #     user.email_user(subject, message)
        # except Exception as e:
        #     print(e)
        #     messages.error(self.request, 'メール送信に失敗しました。')
        # else:
        #     messages.success(self.request, '仮登録しました。メールを確認し本登録を実施してください。')
        return redirect('main:signup')


class ActivateAccount(TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'activateaccount.html'
    timeout_seconds = 60*60*24  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)
        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class Profile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'profile.html'

    def form_valid(self, form):
        messages.success(self.request, '更新が完了しました')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('main:profile', kwargs={'pk': self.kwargs['pk']})


class Setting(LoginRequiredMixin, UpdateView):
    model = AppSettings
    form_class = SettingUpdateForm
    template_name = 'setting.html'

    def form_valid(self, form):
        messages.success(self.request, '更新が完了しました')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('main:setting', kwargs={'pk': self.kwargs['pk']})


@login_required
def subscribe(request):
    appsettings = AppSettings.load()
    client = get_client(appsettings.paypal_client_id,
                        appsettings.paypal_client_secret)

    subscription_id = request.GET.get('subscription_id', None)
    ba_token = request.GET.get('ba_token', None)
    token = request.GET.get('token', None)

    if subscription_id:
        obj = PaypalSubscription.objects.get(subscription_id=subscription_id)
        obj = update_subscription(client, obj)
        obj.ba_token = ba_token
        obj.token = token
        obj.save()
        messages.success(request, '購読処理完了しました')
        return redirect('main:newrequest')

    else:
        plans = list_billing_plans(client)
        active_plans = [p for p in plans if p.status == 'ACTIVE']
        if len(active_plans) == 0:
            messages.error(request, "アクティブなプランが見つかりませんでした。")
            return redirect(reverse("main:newrequest"))

        plan_id = active_plans[0].id
        current_site = get_current_site(request)
        domain = current_site.domain
        return_url = f'http://{appsettings.server_hostname}{reverse("main:subscribe")}' if settings.DJANGO_ENV == 'prod' else 'http://127.0.0.1:8000/subscribe'

        try:
            subscription = create_subscription(
                client, request.user, plan_id, return_url=return_url, cancel_url=return_url)
        except Exception as e:
            print(f'error {e}')
            messages.error(request, str(e))
            return redirect(reverse('main:newrequest'))
        else:
            if not subscription:
                print('subscription is null ')
                messages.error(request, 'サブスクリプション作成に失敗しました。')
                return redirect(reverse('main:newrequest'))
            return redirect(subscription.approve_url)


@login_required
def unsubscribe(request, id):
    appsettings = AppSettings.load()
    client = get_client(appsettings.paypal_client_id,
                        appsettings.paypal_client_secret)

    subscription_id = request.GET.get('subscription_id', None)
    ba_token = request.GET.get('ba_token', None)
    token = request.GET.get('token', None)

    if subscription_id:
        obj = PaypalSubscription.objects.get(subscription_id=subscription_id)
        obj.ba_token = ba_token
        obj.token = token
        obj.save()
        messages.success(request, 'Unsubscrive successful')
        return redirect('main:profile', request.user.id)
    else:
        subscription = PaypalSubscription.objects.get(subscription_id=id)
        subscription = update_subscription(client, subscription)
        if not subscription:
            messages.error(request, 'サブスクリプション更新に失敗しました。')
            return redirect(reverse('main:newrequest'))

        if subscription.status == 'CANCELLED':
            messages.success(request, 'すでにキャンセル済みです。')
            return redirect(reverse('main:newrequest'))

        ret = cancel_subscription(client, subscription)
        if not ret:
            messages.error(request, 'サブスクリプションキャンセルに失敗しました。')
            return redirect(reverse('main:newrequest'))
        messages.success(request, 'サブスクリプションをキャンセルしました。')
        return redirect(reverse('main:newrequest'))


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = PasswordChangeForm
    success_url = reverse_lazy('main:change_password')
    template_name = 'password_change.html'

    def form_valid(self, form):
        messages.success(self.request, 'パスワード変更が完了しました。')
        return super().form_valid(form)


class Top(LoginRequiredMixin, TemplateView):
    template_name = 'top.html'


class CreateScrapeRequest(LoginRequiredMixin, TemplateView):
    template_name = 'scrape_request.html'
    print("__BB____"+template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['use_paypal'] = AppSettings.load().use_paypal
        context['textform'] = RequestTextForm(
        ) if 'textform' not in kwargs else kwargs['textform']
        context['csvform'] = RequestCsvForm(
        ) if 'csvform' not in kwargs else kwargs['csvform']
        return context

    def get(self, *args, **kwargs):
        appsettings = AppSettings.load()
        if appsettings.use_paypal:
            client = get_client(appsettings.paypal_client_id,
                                appsettings.paypal_client_secret)
            if self.request.user.mysubscription:
                update_subscription(client, self.request.user.mysubscription)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        media = self.request.POST.get('media')
        if media == 'text':
            f = RequestTextForm(self.request.POST)
            if not f.is_valid():
                c = self.get_context_data(textform=f)
                return render(self.request, self.template_name, c)
        elif media == 'file':
            f = RequestCsvForm(self.request.POST, self.request.FILES)
            if not f.is_valid():
                c = self.get_context_data(csvform=f)
                return render(self.request, self.template_name, c)
        i = f.save(commit=False)
        i.user = self.request.user
        i.save()
        messages.success(self.request, '登録完了しました.')
        async_process_request(i.id)
        return redirect('main:history')


@login_required
def download(request):
    if request.method == 'GET':
        return HttpResponseBadRequest()

    request_id = request.POST.get('request-id', None)
    encoding = request.POST.get('encoding', None)
    if not request_id or not encoding:
        return HttpResponseBadRequest()
    obj = get_object_or_404(ScrapeRequest, id=request_id)
    results = obj.results.all()
    headers = ScrapeRequestResult.CSV_HEADERS if obj.id_type == 'asin' else ScrapeRequestResult.CSV_HEADERS_JAN
    response = HttpResponse(content_type=f'text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename=download_{datetime.datetime.now().timestamp()}_{encoding}.csv'
    writer = csv.writer(response)
    writer.writerow(headers)
    for r in results:
        elems = r.csv_column_values
        if obj.id_type == 'asin':
            elems[1] = ''
        elif obj.id_type == 'jan':
            temp = elems[0]
            elems[0] = elems[1]
            elems[1] = temp
        writer.writerow([e if e else '' for e in elems])
    return response

@login_required
def delete_request(request, pk):
    if request.method == 'GET':
        return None
    obj = get_object_or_404(ScrapeRequest, pk=pk)
    obj.delete()
    messages.success(request, '削除しました')
    return redirect('main:history')


class ListScrapeRequest(LoginRequiredMixin, ListView):
    model = ScrapeRequest
    template_name = 'request_list.html'
    paginate_by = 10

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).order_by('-requested_at')


class ListScrapeRequestResult(LoginRequiredMixin, ListView):
    model = ScrapeRequestResult
    template_name = 'scrape_result_list.html'
    paginate_by = 10

    def get_queryset(self):
        return self.model.objects.filter(scrape_request__user=self.request.user).order_by('-id')
