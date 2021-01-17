# edgarapp/models.py
# for database
# @radiasl

from django.db import models

class Quarterly(models.Model):

	quarterly = models.CharField(max_length=255)
	url = models.CharField(max_length=255)
	cik = models.IntegerField()
	error = models.CharField(max_length=255)
	date = models.DateTimeField()
	filing = models.CharField(max_length=255)

	def __str__(self):
		return self.quarterly
	


class Company(models.Model):
	cik = models.CharField(max_length=255)
	ticker = models.CharField(max_length=10)
	name = models.CharField(max_length=255)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['cik', 'name'], name='cik_name constraint')
		]

		indexes = [
			models.Index(fields=['ticker'])
		]

	def __str__(self):
		return self.name

class CS_Rel(models.Model):
	id = models.IntegerField(primary_key=True)
	ticker1 = models.CharField(max_length=50, blank=True, null=True)
	ticker2 = models.CharField(max_length=50, blank=True, null=True)
	company = models.CharField(max_length=50, blank=True, null=True)
	supplier = models.CharField(max_length=50, blank=True, null=True)

	def __str__(self):
		return self.ticker1 + ' : ' + self.ticker2
	
class Filing(models.Model):
	cik = models.CharField(max_length=255)
	name = models.CharField(max_length=255)
	filingtype = models.CharField(max_length=255)
	filingdate = models.CharField(max_length=255)
	filingpath = models.CharField(max_length=255) # local file path

	company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='filings')

	class Meta:
		
		ordering = ('-filingdate',)

		constraints = [
			models.UniqueConstraint(fields=['filingpath','filingdate'], name='path_date constraint')
		]

	def __str__(self):
		return self.name

	def dict_values(self):

		return {
			'id': self.id,
			'type': self.filingtype,
			'date': self.filingdate
		}


class Funds(models.Model):
	fund = models.CharField(max_length=255)
	company = models.CharField(max_length=255)
	classTitle = models.CharField(max_length=255)
	CUSIP = models.CharField(max_length=255)
	value = models.CharField(max_length=255)
	share_prn_amount = models.CharField(max_length=255)
	share_prn_type = models.CharField(max_length=255)
	put_call = models.CharField(max_length=255)
	investment_discretion = models.CharField(max_length=255)
	other_manager = models.CharField(max_length=255)
	sole_voting_authority = models.CharField(max_length=255)
	shared_voting_authority = models.CharField(max_length=255)
	none_voting_authority = models.CharField(max_length=255)

	company_rep = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='funds')

	class Meta:

		ordering = ('-value',)


class Directors(models.Model):
	company = models.CharField(max_length=255)
	director = models.CharField(max_length=255)
	age = models.CharField(max_length=255)
	bio = models.CharField(max_length=255)

	company_rep = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='company_directors')

	other_companies = models.ManyToManyField(Company, blank=True)

	class Meta:

		ordering = ('-director',)


class Proxies(models.Model):
	cik = models.CharField(max_length=255)
	name = models.CharField(max_length=255)
	filingtype = models.CharField(max_length=255)
	filingdate = models.CharField(max_length=255)
	filingpath = models.CharField(max_length=255) # local file path

	company_rep = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='proxies')

class Executives(models.Model):
	company = models.CharField(max_length=255)
	executives = models.CharField(max_length=255)
	filingdate = models.CharField(max_length=255)

	company_rep = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='executives')
	


class FilingTOC(models.Model):
	body = models.TextField()
	filing = models.ForeignKey(Filing, on_delete=models.SET_NULL,null=True, related_name='table_of_contents')
class FilingsExhibits(models.Model):
	exhib_type = models.CharField(max_length=255)
	exhib_date = models.CharField(max_length=255)
	exhib_path = models.CharField(max_length=255)
	company_cik = models.CharField(max_length=255)

	def __str__(self):
		return self.company_cik

class ProxyTOC(models.Model):
	body = models.TextField()
	proxy = models.ForeignKey(Proxies, on_delete=models.SET_NULL,null=True, related_name='table_of_contents')
