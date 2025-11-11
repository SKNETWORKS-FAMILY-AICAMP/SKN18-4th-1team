from django.db import models


class Disease(models.Model):
    SEVERITY_CHOICES = [
        ('low', '경증'),
        ('medium', '중등도'),
        ('high', '중증'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='질병명')
    description = models.TextField(verbose_name='설명')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, verbose_name='중증도')
    
    class Meta:
        verbose_name = '질병'
        verbose_name_plural = '질병들'
    
    def __str__(self):
        return self.name


class DiseaseRecommendation(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='recommendations', verbose_name='질병')
    recommendation = models.CharField(max_length=500, verbose_name='권장사항')
    
    class Meta:
        verbose_name = '질병 권장사항'
        verbose_name_plural = '질병 권장사항들'
    
    def __str__(self):
        return f"{self.disease.name} - {self.recommendation}"


class Hospital(models.Model):
    name = models.CharField(max_length=200, verbose_name='병원명')
    specialty = models.CharField(max_length=100, verbose_name='진료과')
    address = models.CharField(max_length=300, verbose_name='주소')
    phone = models.CharField(max_length=20, verbose_name='전화번호')
    distance = models.CharField(max_length=50, verbose_name='거리', default='')
    wait_time = models.CharField(max_length=50, verbose_name='대기시간', default='')
    
    class Meta:
        verbose_name = '병원'
        verbose_name_plural = '병원들'
    
    def __str__(self):
        return self.name


class SymptomKeyword(models.Model):
    keyword = models.CharField(max_length=100, verbose_name='키워드')
    diseases = models.ManyToManyField(Disease, verbose_name='관련 질병들')
    hospitals = models.ManyToManyField(Hospital, verbose_name='추천 병원들')
    
    class Meta:
        verbose_name = '증상 키워드'
        verbose_name_plural = '증상 키워드들'
    
    def __str__(self):
        return self.keyword

