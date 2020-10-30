
from random import random, choice, seed

import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
from math import ceil,floor,exp

seed(datetime.now())

def main():
    Marcas = ["Marca1","Marca2","Marca3","Marca4"]
    Cereales = Category(Marcas)
    Cereales.set_sales_percent([10,20,30,40])
    
    Cereales.set_new_brand("MarcaA")
    Cereales.set_new_brand_canibalization_ratios([0.05,0.05,0.05,0.1])
                
    unitsBrandMonth = Cereales.simulate_sales_allbrands(270) #5 year in weeks           
    
    brands = Cereales.allBrands
    meses = range(Cereales.numberMonths)
    numberBrands = Cereales.numberBrands
    
    penetrationXBrand = Cereales.get_penetration_x_brand()
    
    colorMapFunct = get_cmap(numberBrands*2)
    fig, axs = plt.subplots(numberBrands, 1,figsize=(8,6))        
    for idx, penetrationRat in enumerate(penetrationXBrand):
        axs[idx].plot(meses, penetrationRat,color= colorMapFunct(idx))
        axs[idx].set_ylabel(brands[idx])
        if idx==0 :
            axs[idx].set_title("Indice de penetracion ")                       
        if idx<(numberBrands-1):                                    
            axs[idx].set_xticks([])            
    fig.savefig("indice_penetracion.png")  
    fig.clf()    
    
    monthsWithNewBrandSales = len([x for x in penetrationXBrand[-1] if x>0])
    
    gridCols = 5
    fig, axs = plt.subplots(numberBrands, gridCols,figsize=(8,6))
           
    PenetrationIndexMarcaExt = penetrationXBrand[-1][0:monthsWithNewBrandSales-1]
    meanPenetrationIndexMarcaExt=sum(PenetrationIndexMarcaExt)/len(PenetrationIndexMarcaExt)
    
    print("Indice de pentracion para")
    print("        Sin MA  Con MA  Can")    
    
    for idx, penetrationRat in enumerate(penetrationXBrand):
        penetrationOdered = [x for x,new_brand in zip(penetrationRat,penetrationXBrand[-1]) if new_brand>0]+ \
        [x for x,new_brand in zip(penetrationRat,penetrationXBrand[-1]) if new_brand<=0]
        color_plot = colorMapFunct(idx)
        axs[idx,0] = plt.subplot2grid((numberBrands, gridCols), (idx, 0), colspan=gridCols-1)
        axs[idx,0].plot(meses, penetrationOdered, color= color_plot)
        axs[idx,0].axvline(x=monthsWithNewBrandSales, color="grey", linestyle = "--")        
        axs[idx,0].set_ylabel(brands[idx])
        
        PenetrationIndexWith = penetrationOdered[0:monthsWithNewBrandSales-1]
        meanPenetrationIndexWith=sum(PenetrationIndexWith)/len(PenetrationIndexWith)
        
        PenetrationIndexWithout = penetrationOdered[monthsWithNewBrandSales:]
        meanPenetrationIndexWithout=sum(PenetrationIndexWithout)/len(PenetrationIndexWithout)
        
        expectedPenetrationIndex = meanPenetrationIndexWithout*(1-meanPenetrationIndexMarcaExt)
        diffPenetrationIndex = expectedPenetrationIndex-meanPenetrationIndexWith
        CanibalizationIndex = 0
        try:
            CanibalizationIndex = (meanPenetrationIndexWithout-meanPenetrationIndexWith)/meanPenetrationIndexWithout
        except:
            pass
        print("%s  %.3f   %.3f   %.3f" % (brands[idx],meanPenetrationIndexWithout,meanPenetrationIndexWith,  CanibalizationIndex))
        
        axs[idx,gridCols-1].hist(PenetrationIndexWith,orientation='horizontal', color= colorMapFunct(0), alpha=0.5)        
                    
        ylimLeftPlot = axs[idx,0].get_ylim()
        axs[idx,gridCols-1].set_ylim(ylimLeftPlot)
            
        axs[idx,gridCols-1].set_yticks([])
        
        if idx==0 :
            axs[idx,0].set_title("Indice de penetracion (semanas con/sin %s)" % brands[-1])
            axs[idx,gridCols-1].set_title("Histograma")
            
        if idx<(numberBrands-1):                        
            axs[idx,gridCols-1].hist(penetrationOdered[monthsWithNewBrandSales:],orientation='horizontal', color= colorMapFunct(numberBrands), alpha=0.5)
            axs[idx,0].set_xticks([])
            axs[idx,gridCols-1].set_xticks([])
        
    #fig.suptitle('Indice de Penetración')    
    fig.savefig("indice_penetracion_ordenado.png")  
    fig.clf()        
    
    
class Category:    
    def __init__(self,BNames=[]):
        self.BrandsNames=BNames                
        self.numberOfBrands = len(self.BrandsNames)
        self.salesPercent = [1.0/self.numberOfBrands]*self.numberOfBrands      
        self.canibalizationRatios = [0.0]*self.numberOfBrands  
        
        self.allBrands = []
        self.numberMonths = 0
        self.numberBrands = 0
        
        self.penetrationXBrand = []
        
    def get_names(self):
        return self.BrandsNames
        
    def set_sales_percent(self,percents):   
        iterablePercents = return_iterable_value(percents)
        for index, percent in enumerate(iterablePercents):
            if  percent>=0:
                self.salesPercent[index] = percent                
            else :           
                print("Percentage must be a positive number")
                               
        self.normalize_sales_percent()    
            
    def set_new_brand(self,newbrandName):        
        self.newBrand = newbrandName
        self.newBrandOn = True
    
    def set_new_brand_canibalization_ratios(self,percents):                
        iterablePercents = return_iterable_value(percents)
        for index, percent in enumerate(iterablePercents):
            if  percent>=0:
                self.canibalizationRatios[index] = percent                
            else :            
                print("Percentage must be a positive number")
                             
    def normalize_sales_percent(self):
        sumPercentage = sum(self.salesPercent)
        if sumPercentage>0 :
            for index in range(self.numberOfBrands):
                self.salesPercent[index]=self.salesPercent[index]/sumPercentage
        else : #If somethign if wrong set all percentage equal
            self.salesPercent = [1.0/self.numberOfBrands]*self.numberOfBrands
                      
    def __new_product_canibalization_posible(self,id):
        return (self.canibalizationRatios[id] > 0 and self.newBrandOn) 
        
    def get_sales_percents(self):
        return self.salesPercent
    
    def turn_on_new_brand(self,turnOnOff):
        self.newBrandOn = turnOnOff
    
    def pick_random_brand(self): 
        random_event = random()    
        lowPercent = 0
        highPercent = 0
        idBrandChose = -1
        for index in range(self.numberOfBrands):
            highPercent += self.salesPercent[index]
            if random_event >= lowPercent and random_event < highPercent:               
                idBrandChose = index                                    
                break
            lowPercent += self.salesPercent[index]
        
        brandChoice = self.BrandsNames[idBrandChose]
        if self.__new_product_canibalization_posible(idBrandChose):
            random_event = random()
            if random_event <= self.canibalizationRatios[idBrandChose]:
                brandChoice =  self.newBrand   
        
        return brandChoice
    
    def simulate_multiple_sales(self,Number_sales):
        brandCumulative = []
        brandNames      = []
        for _ in range(Number_sales):
            brand_choice = self.pick_random_brand()
            if not(brand_choice in brandNames):
                brandNames.append(brand_choice)
                brandCumulative.append(0)
                
            idx = brandNames.index(brand_choice)
            brandCumulative[idx] += 1
        returnArray = [(x[0],x[1]) for x in zip(brandNames,brandCumulative)]
        return returnArray
        
    def simulate_sales_allbrands(self,Nmonths=12):
        monthSales = self.get_simulated_units(Nmonths) #5 year in weeks
    
        unitsBrandMonth = []    
        for id_mes, sales in enumerate(monthSales):     
            self.turn_on_new_brand(choice([True,False]))
            simulatedSales = self.simulate_multiple_sales(sales)    
            sumBrandCumulative = sum([x[1] for x in simulatedSales])
        
            for brand,count in simulatedSales:
                #print(id_mes, brand, count,"%.3f" % (count/sumBrandCumulative))
                unitsBrandMonth.append([id_mes, brand, count,count/sumBrandCumulative])
        
        self.allBrands = sorted(list(set([x[1] for x in unitsBrandMonth])))
        self.numberMonths = len(set([x[0] for x in unitsBrandMonth]))
        self.numberBrands = len(self.allBrands)
                
        self.penetrationXBrand = []        
        for brand in self.allBrands:
            penetrationRat = []
            for idMonth in range(self.numberMonths):
                arrPenetration = [x[3]  for x in unitsBrandMonth if (x[0] == idMonth and x[1] == brand)]
                if len(arrPenetration)>0:
                    penetrationRat.append(sum(arrPenetration)/len(arrPenetration))
                else :
                    penetrationRat.append(0)
            self.penetrationXBrand.append(penetrationRat)
                
        return unitsBrandMonth
        
    def get_penetration_x_brand(self):
        return self.penetrationXBrand
        
    def get_simulated_units(self,Nmonts =12):
        baseUnits = 800
        growRate  = 30
        seasonalAmount  = 1500
        monthDistribution = [28,25,29,32,34,30,28,26,25,28,35,33]
        monthDistribution = normalize_array(monthDistribution)
        
        meses = np.arange(0,Nmonts,1)
        unidadesVendidas = [int(growRate*x*(0.9+0.3*random())/12 + baseUnits+seasonalAmount*monthDistribution[x%12]) for x in meses]

        return unidadesVendidas   
        
def return_iterable_value(val):
    valueToReturn = val
    #Strings are iterable so we return [val] when val is str
    if type(val) == type("sampleString") or not(hasattr(val, '__iter__')):
        valueToReturn = [val]
    else :
        valueToReturn = val
    return (valueToReturn)

def normalize_array(arr):
    cumsum = sum(arr)
    return_arr = [ ]
    for x in arr:
       return_arr.append(x/cumsum)
    return return_arr
 
def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)
 
def plot_historical_units():   
    numeroMeses = 36
    meses = np.arange(0,numeroMeses,1)# range(36)
    unidadesVendidas = np.array(get_simulated_units(numeroMeses))
    
    plt.scatter(meses, unidadesVendidas)
    plt.title('Unidades vendidas')
    plt.xlabel('Semanas')
    plt.ylabel('Unidades')
    plt.savefig("unit_sales.png")    

def get_simulated_units(Nmonts =12):
    baseUnits = 800
    growRate  = 30
    seasonalAmount  = 1500
    monthDistribution = [28,25,29,32,34,30,28,26,25,28,35,33]
    monthDistribution = normalize_array(monthDistribution)
    
    meses = np.arange(0,Nmonts,1)
    unidadesVendidas = [int(growRate*x*(0.9+0.3*random())/12 + baseUnits+seasonalAmount*monthDistribution[x%12]) for x in meses]

    return unidadesVendidas    
        
if __name__ == "__main__":
    main()