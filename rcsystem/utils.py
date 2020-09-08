import time

from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import management
from django.utils import timezone


class ItemViewMixin:
    model = None
    template = None
    context_name = None

    def get(self, request):
        all_items = self.model.objects.all()[:30]
        item_page_1 = request.GET.get('page', 1)
        paginator = Paginator(all_items, 10)
        try:
            items = paginator.page(item_page_1)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(request, self.template, context={self.context_name: items})


class ItemAddView:
    Form = None
    item_name = None

    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('recommender:index'))

        form = self.Form()
        return render(request, "add_item.html", {"form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('recommender:index'))

        form = self.Form(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('recommender:index'))
        else:
            form = self.Form()

        with open("rcsystem/static/" + self.item_name + "_dataset.csv", "a") as f:
            # should save to dataset but it is too long
            pass

        management.call_command("train_models", which=self.item_name)

        return render(request, "add_item.html", {"form": form})


class ItemDetailView:
    model = None
    model_ratings = None
    template = None
    item_name = None
    item_name_singular = None
    dataset = None
    cosine_sim = None

    def get(self, request, pk):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return HttpResponseRedirect(reverse('recommender:index'))

        is_rated = 0
        if request.user.is_authenticated:
            try:
                if self.item_name == "books":
                    is_rated = self.model_ratings.objects.get(user_id=request.user.id, book_id=pk).rating
                elif self.item_name == "movies":
                    is_rated = self.model_ratings.objects.get(user_id=request.user.id, movie_id=pk).rating
            except self.model_ratings.DoesNotExist:
                pass

        if self.item_name == "movies" and item.movie_index >= 10000:
            context = {
                'movie': item,
                'recommend_movies': "recommend_movies",
                'is_rated': is_rated,
                'user': request.user
            }
            return render(request, 'movie_recommend.html', context=context)

        recommend_items = tuple(self.get_recommendations(item.title))
        if self.item_name == "books":
            recommend_items = self.model.objects.filter(pk__in=recommend_items)
        elif self.item_name == "movies":
            recommend_items = self.model.objects.filter(movie_index__in=recommend_items)

        context = {
            self.item_name_singular: item,
            'recommend_' + self.item_name: recommend_items,
            'is_rated': is_rated,
            'user': request.user
        }
        return render(request, self.template, context=context)

    def get_index_from_title(self, title):
        if self.item_name == "movies":
            return self.dataset[self.dataset["title"] == title].index[0]
        return self.dataset[self.dataset["title"] == title]["id"].values[0]

    def get_recommendations(self, title):
        idx = int(self.get_index_from_title(title))
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]
        item_indices = [i[0] for i in sim_scores]
        return self.dataset['title'].iloc[item_indices].index.tolist()

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('recommender:index'))

        rated = int(request.POST["rating"])
        if self.item_name == "books":
            rating = self.model_ratings(rating=rated, book_id=pk, user_id=request.user.id)
            rating.save()
        elif self.item_name == "movies":
            date = str(timezone.now())
            rating = self.model_ratings(user_id=request.user.id, rating=rated, movie_id=pk, timestamp=date)
            rating.save()

        with open("rcsystem/static/" + self.item_name + "_ratings.csv", "a") as f:
            if self.item_name == "books":
                append = str(pk) + "," + str(request.user.id) + "," + str(rated) + "\n"
            elif self.item_name == "movies":
                append = str(request.user.id) + "," + str(pk) + "," + str(rated) + "," + str(int(time.time())) + "\n"
            f.write(append)

        user_rated_items = self.model_ratings.objects.filter(user_id=request.user.id)
        if len(user_rated_items) % 5 == 0:
            management.call_command("train_models", which=self.item_name + "_rated")

        return HttpResponseRedirect(request.path_info)
