from django.db.models import Q
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum
from django.db.models import Count
from .models import TableStat, TableUsers, UsersShtat
from .forms import ChangeStatusUsers, AddUsers, CategoryForm
from .send_pdf import send_email
from django.views.generic import View
from .utils import ObjectUpdateMixin, ObjectDeleteMixin, render_to_pdf
from django.contrib.auth.mixins import LoginRequiredMixin
import time, os


# For pdf
from django.http import HttpResponse
from django_xhtml2pdf.utils import fetch_resources, generate_pdf
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from django.contrib import messages
# Create your views here.


def home_page(request):
    time_day = time.strftime("%d.%m.%Y", time.localtime())
    
    # Для COVID-19
    table_users_all = TableUsers.objects.all()
    status = TableStat.objects.all()
    category_top = status.filter(Q(check_top_category=1) | Q(
        check_top_category=2) | Q(check_top_category=3) | Q(check_top_category=4))
    category_down = status.exclude(Q(check_top_category=1) | Q(
        check_top_category=2) | Q(check_top_category=3) | Q(check_top_category=4))
    # print(category_down.filter('tableusers_set'))

    # По штату
    user_shtat = UsersShtat.objects.all()
    user_shtat_all = user_shtat.aggregate(Sum('count_shtat'))
    user_shtat_one = user_shtat.get(name=1).count_shtat
    user_shtat_two = user_shtat.get(name=2).count_shtat
    user_shtat_tree = user_shtat.get(name=3).count_shtat

    # По факту
    st_users = TableUsers.objects.all()
    st_users_all = st_users.count()
    st_users_one = st_users.filter(user_category=1).count()
    st_users_two = st_users.filter(user_category=2).count()
    st_users_atest=st_users_one+st_users_two
    st_users_tree = st_users.filter(user_category=3).count()
    # Отсутствуют
    otsutstvujut = st_users.exclude(Q(user_status__check_top_category=1) |
                                    Q(user_status__check_top_category=2) |
                                    Q(user_status__check_top_category=3) |
                                    Q(user_status__check_top_category=4))
    # print(otsutstvujut)
    v_stroju = st_users.filter(Q(user_status__check_top_category=1) |
                                Q(user_status__check_top_category=2))
    # Всего по штату
    # user_shtat_all['count_shtat__sum']

    # Всего некомплект
    nekompl_all = user_shtat_all['count_shtat__sum'] - st_users_all
    # средний и старший НC некомплект
    nekompl_shtat_one = user_shtat_one - st_users_one
    # рядовой и младший НС некомлпект
    nekompl_shtat_two = user_shtat_two - st_users_two
    # служащие некомплект
    nekompl_shtat_tree = user_shtat_tree - st_users_tree
    # аттестованные некомплект
    nekompl_atest = nekompl_shtat_one + nekompl_shtat_two

    # Подпись
    sign = TableUsers.objects.filter(users_sign=True)

    context = {
        'otsutstvujut': otsutstvujut,
        'v_stroju': v_stroju,
        'category_top': category_top,
        'category_down': category_down,
        'status': status,
        'sign': sign,
        'time_day': time_day,
        'table_users_all': table_users_all,
        'st_users_all': st_users_all,
        'user_shtat_one': user_shtat_one,
        'user_shtat_two': user_shtat_two,
        'user_shtat_tree': user_shtat_tree,
        'user_shtat_all': user_shtat_all,
        'st_users_one': st_users_one,
        'st_users_two': st_users_two,
        'st_users_tree': st_users_tree,
        'nekompl_all': nekompl_all,
        'nekompl_shtat_one': nekompl_shtat_one,
        'nekompl_shtat_two': nekompl_shtat_two,
        'nekompl_shtat_tree': nekompl_shtat_tree,
        'nekompl_atest': nekompl_atest,
    }
    return render(request, 'table_in/index.html', context)
    

class StatusChange(View):
    def get(self, request, queryset=None):
        status_us = TableUsers.objects.filter()
        status_form = ChangeStatusUsers()
        return render(request, 'table_in/status_change.html', context={'form': status_form, 'status_us': status_us})


class CreateFields(View):
    def get(self, request):
        form = AddUsers()
        return render(request, 'table_in/create_fields.html', context={'form': form})

    def post(self, request):
        bound_form = AddUsers(request.POST)

        if bound_form.is_valid():
            new_form = bound_form.save()
            return redirect(home_page)
        return render(request, 'table_in/create_fields.html', context={'form': bound_form})


def list_users(request):
    list_users_all = TableUsers.objects.all()
    sign = TableUsers.objects.filter(users_sign=True)
    return render(request, 'table_in/lists_users.html',
                  {
                      'list_users_all': list_users_all,
                      'sign': sign,
                  }
                  )


# VIEWS LISTS CATEGORY
def list_category(request):
    list_category_all = TableStat.objects.all()
    # list_category_not_lost = TableStat.objects.filter(users_sign=True)
    return render(request, 'table_in/list_category.html',
                  {
                      'list_category_all': list_category_all,
                  }
                  )


class CategoryUpdate(ObjectUpdateMixin, View):
    model = TableStat
    model_form = CategoryForm
    template = 'table_in/list_category_edit.html'
    raise_exception = True
    fields_form = 'категории'
    redirect_url = 'list_category_url'


class CategoryCreate(View):
    def get(self, request):
        form = CategoryForm()
        return render(request, 'table_in/create_category.html', context={'form': form})
    
    def post(self, request):
        bound_form = CategoryForm(request.POST)

        if bound_form.is_valid():
            new_form = bound_form.save()
            return redirect(list_category)
        return render(request, 'table_in/create_category.html', context={'form': bound_form})


class CategoryDelete(ObjectDeleteMixin, View):
    model = TableStat
    template = 'table_in/delete_category.html'
    redirect_url = 'list_category_url'
    raise_exception = True


# LoginRequiredMixin,
class UsersUpdate(ObjectUpdateMixin, View):
    model = TableUsers
    model_form = AddUsers
    template = 'table_in/update_users.html'
    raise_exception = True
    fields_form = 'профиля'
    redirect_url = 'list_users_url'


class UsersDelete(ObjectDeleteMixin, View):
    model = TableUsers
    template = 'table_in/delete_users.html'
    redirect_url = 'home_page'
    raise_exception = True


# PDF PREVIEW
def pdf_generate(request):
    resp = HttpResponse(content_type='application/pdf')
    
    time_day = time.strftime("%d.%m.%Y", time.localtime())

    # Для COVID-19
    table_users_all = TableUsers.objects.all()
    status = TableStat.objects.all()
    category_top = status.filter(Q(check_top_category=1) | Q(
        check_top_category=2) | Q(check_top_category=3) | Q(check_top_category=4))
    category_down = status.exclude(Q(check_top_category=1) | Q(
        check_top_category=2) | Q(check_top_category=3) | Q(check_top_category=4))
    # print(category_down.filter('tableusers_set'))

    # По штату
    user_shtat = UsersShtat.objects.all()
    user_shtat_all = user_shtat.aggregate(Sum('count_shtat'))
    user_shtat_one = user_shtat.get(name=1).count_shtat
    user_shtat_two = user_shtat.get(name=2).count_shtat
    user_shtat_tree = user_shtat.get(name=3).count_shtat

    # По факту
    st_users = TableUsers.objects.all()
    st_users_all = st_users.count()
    st_users_one = st_users.filter(user_category=1).count()
    st_users_two = st_users.filter(user_category=2).count()
    st_users_tree = st_users.filter(user_category=3).count()
    # Отсутствуют
    otsutstvujut = st_users.exclude(Q(user_status__check_top_category=1) |
                                    Q(user_status__check_top_category=2) |
                                    Q(user_status__check_top_category=3) |
                                    Q(user_status__check_top_category=4))
    # print(otsutstvujut)
    v_stroju = st_users.filter(Q(user_status__check_top_category=1) |
                               Q(user_status__check_top_category=2))
    # Всего по штату
    # user_shtat_all['count_shtat__sum']

    # Всего некомплект
    nekompl_all = user_shtat_all['count_shtat__sum'] - st_users_all
    # средний и старший НC некомплект
    nekompl_shtat_one = user_shtat_one - st_users_one
    # рядовой и младший НС некомлпект
    nekompl_shtat_two = user_shtat_two - st_users_two
    # служащие некомплект
    nekompl_shtat_tree = user_shtat_tree - st_users_tree
    # аттестованные некомплект
    nekompl_atest = nekompl_shtat_one + nekompl_shtat_two

    # Подпись
    sign = TableUsers.objects.filter(users_sign=True)

    context = {
        'otsutstvujut': otsutstvujut,
        'v_stroju': v_stroju,
        'category_top': category_top,
        'category_down': category_down,
        'status': status,
        'sign': sign,
        'time_day': time_day,
        'table_users_all': table_users_all,
        'st_users_all': st_users_all,
        'user_shtat_one': user_shtat_one,
        'user_shtat_two': user_shtat_two,
        'user_shtat_tree': user_shtat_tree,
        'user_shtat_all': user_shtat_all,
        'st_users_one': st_users_one,
        'st_users_two': st_users_two,
        'st_users_tree': st_users_tree,
        'nekompl_all': nekompl_all,
        'nekompl_shtat_one': nekompl_shtat_one,
        'nekompl_shtat_two': nekompl_shtat_two,
        'nekompl_shtat_tree': nekompl_shtat_tree,
        'nekompl_atest': nekompl_atest,
    }
    #print('Debug info:', 'table_in/index_pdf.html', resp, context)
    result = generate_pdf('table_in/index_pdf.html',
                          file_object=resp, context=context)
    return result

# PDF GENERATE AND SEND
class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        time_day = time.strftime("%d.%m.%Y", time.localtime())

        # Для COVID-19
        table_users_all = TableUsers.objects.all()
        status = TableStat.objects.all()
        category_top = status.filter(Q(check_top_category=1) | Q(
            check_top_category=2) | Q(check_top_category=3) | Q(check_top_category=4))
        category_down = status.exclude(Q(check_top_category=1) | Q(
            check_top_category=2) | Q(check_top_category=3) | Q(check_top_category=4))
        # print(category_down.filter('tableusers_set'))

        # По штату
        user_shtat = UsersShtat.objects.all()
        user_shtat_all = user_shtat.aggregate(Sum('count_shtat'))
        user_shtat_one = user_shtat.get(name=1).count_shtat
        user_shtat_two = user_shtat.get(name=2).count_shtat
        user_shtat_tree = user_shtat.get(name=3).count_shtat

        # По факту
        st_users = TableUsers.objects.all()
        st_users_all = st_users.count()
        st_users_one = st_users.filter(user_category=1).count()
        st_users_two = st_users.filter(user_category=2).count()
        st_users_tree = st_users.filter(user_category=3).count()
        # Отсутствуют
        otsutstvujut = st_users.exclude(Q(user_status__check_top_category=1) |
                                        Q(user_status__check_top_category=2) |
                                        Q(user_status__check_top_category=3) |
                                        Q(user_status__check_top_category=4))
        # print(otsutstvujut)
        v_stroju = st_users.filter(Q(user_status__check_top_category=1) |
                                Q(user_status__check_top_category=2))
        # Всего по штату
        # user_shtat_all['count_shtat__sum']

        # Всего некомплект
        nekompl_all = user_shtat_all['count_shtat__sum'] - st_users_all
        # средний и старший НC некомплект
        nekompl_shtat_one = user_shtat_one - st_users_one
        # рядовой и младший НС некомлпект
        nekompl_shtat_two = user_shtat_two - st_users_two
        # служащие некомплект
        nekompl_shtat_tree = user_shtat_tree - st_users_tree
        # аттестованные некомплект
        nekompl_atest = nekompl_shtat_one + nekompl_shtat_two

        # Подпись
        sign = TableUsers.objects.filter(users_sign=True)

        context = {
            'otsutstvujut': otsutstvujut,
            'v_stroju': v_stroju,
            'category_top': category_top,
            'category_down': category_down,
            'status': status,
            'sign': sign,
            'time_day': time_day,
            'table_users_all': table_users_all,
            'st_users_all': st_users_all,
            'user_shtat_one': user_shtat_one,
            'user_shtat_two': user_shtat_two,
            'user_shtat_tree': user_shtat_tree,
            'user_shtat_all': user_shtat_all,
            'st_users_one': st_users_one,
            'st_users_two': st_users_two,
            'st_users_tree': st_users_tree,
            'nekompl_all': nekompl_all,
            'nekompl_shtat_one': nekompl_shtat_one,
            'nekompl_shtat_two': nekompl_shtat_two,
            'nekompl_shtat_tree': nekompl_shtat_tree,
            'nekompl_atest': nekompl_atest,
        }
        # pdf = generate_pdf('table_in/index_pdf.html', context)
        date_year = f'{time.strftime("%Y", time.localtime())}'
        date_month = f'{time.strftime("%m-%Y", time.localtime())}'
        date_pdf = f'{time.strftime("%Y-%m-%d", time.localtime())}'
        name_pdf = f'{date_pdf} Строевая записка отдела ТПСЭД ЦАиТП.pdf'

        # link = rf'\\zh-srv-store-1.guin.gov\OTPIS\_!Отчеты\Кто в отпуске для строевки ОТПИС (lapina.g.d@fsin.uis)\{date_year}\{date_month}\{name_pdf}'
        # link_dirs = rf'\\zh-srv-store-1.guin.gov\OTPIS\_!Отчеты\Кто в отпуске для строевки ОТПИС (lapina.g.d@fsin.uis)\{date_year}\{date_month}'

        link = os.path.abspath(os.path.join("../../stroevaya_zapiska/", date_year, date_month, name_pdf))
        link_dirs = os.path.abspath(os.path.join("../../stroevaya_zapiska/", date_year, date_month))

        if os.path.exists(link_dirs) is False:
            os.makedirs(link_dirs)
            while os.path.isdir(link_dirs) is False:
                time.sleep(1)

        if os.path.realpath(link):
            with open(link, 'wb') as output:
                template = get_template('table_in/index_pdf.html')
                html = template.render(context)

                try:
                    pdf = pisa.CreatePDF(html.encode("UTF-8"),
                                    output, encoding='UTF-8', link_callback=fetch_resources)
                except Exception as e:
                    print(f'Error during PDF creation: {e}')
                    print(html)
                send_email(link, name_pdf)
                messages.success(request, 'PDF сформирован и отправлен!')
        return redirect('home_page')
        # return pdf
