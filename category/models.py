from django.db import models


class CategoryModel(models.Model):
    category = models.TextField(max_length=100, default='')
    fa_name = models.TextField(max_length=50, null=True, blank=True, default='')
    sid = models.TextField(max_length=50, default='')
    link = models.TextField(max_length=3000, null=True, blank=True, default='')
    short_cut = models.TextField(max_length=50, null=True, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    deleted = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return str(self.category)


class SubCategoryModel(models.Model):
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE, related_name='sub', default='')
    main_title = models.TextField(max_length=100, null=True, blank=True, default='')
    full_title = models.TextField(max_length=100, null=True, blank=True, default='')
    short_title = models.TextField(max_length=50, null=True, blank=True, default='')
    link = models.TextField(max_length=3000, null=True, blank=True, default='')
    home = models.TextField(max_length=100, null=True, blank=True, default='')
    vname = models.TextField(max_length=100, null=True, blank=True, default='')
    html = models.TextField(
        max_length=30000,
        null=True,
        blank=True,
        default=
        """<div class="col-md-5">
                <div class="card">
                    <div class="card-header">
                        <h5 class="title">
                            Important updates posted sooner than you expect – stay connected!
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="toolbar">
                            <h6>
                                Any Suggestions or Complaints?  
                                <a href="/contact/" class="text-info text-capitalize">Contact Us</a>
                            </h6>
                        </div>
                    </div>
                </div>
            </div>"""
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    deleted = models.BooleanField(default=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.full_title:
            self.full_title = self.main_title
        if not self.short_title and self.full_title:
            self.short_title = self.full_title[:2]
        if not self.home:
            self.home = self.main_title
        if not self.vname:
            self.vname = self.full_title
        super().save(*args, **kwargs)

    def __str__(self):
        return str(f'{self.main_title} {self.link}')


class SubCategoryTextModel(models.Model):
    sub = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE, related_name='sub_category', default='')
    text = models.TextField(max_length=3000, null=True, blank=True, default='')
    link = models.TextField(max_length=3000, null=True, blank=True, default='')
    link_text = models.TextField(max_length=3000, null=True, blank=True, default='')
    html = models.TextField(max_length=30000, null=True, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    deleted = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return str(f'{self.sub} | {self.link}')
