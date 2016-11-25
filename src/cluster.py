import random , string, copy
import pylab

class Point(object):
    """Point is the data to be clustered"""
    def __init__(self, name, Features, label = None ):
        """normalizedAttrs and originalAttrs are both lists"""
        self.name = name 
        self.Features = Features
        self.label = label
    def dimensionality (self):
        return len(self.Features)
    def getFeatures(self):
        return self.Features[:]
    def getLabel(self):
        return self.label 
    def distance(self, other):
        #distance function is used to calculate the euclidean distance between two points
        result = 0.0 
        for i in range(self.dimensionality()):
            result = result + (self.Features[i]-other.Features[i])**2   #euclidean distance formular 
        return result ** 0.5
    def getName(self):
        return self.name
    def toStr(self):
        return self.name +str(self.Features)
    def __str__(self):
        return self.name + ':' + str(self.Features) + ':' + str(self.label)


class Cluster(object) :
      """points are list of object of type Point defined above , they are the points in a cluster """
      def __init__(self, points):
          self.points = points 
          self.centroid = self.computeCentroid()
      def addlabel(self,label):
          self.label = label
          
      def singleLinkageDist(self, other) :
          minDist = self.points[0].distance(other.points[0])
          for p1 in self.points :
              for p2 in other.points :
                  if p1.distance(p2)<minDist :
                      minDist = p1.distance(p2)
          return minDist 
      def maxLinkageDist (self, other) :
          maxDist = self.points[0].distance(other.points[0])
          for p1 in self.points:
              for p2 in other.points :
                  if p1.distance(p2)>maxDist :
                      maxDist = p1.distance(p2)
          return maxDist
      def averageLinkageDist(self, other):
          totdist = 0.0 
          for p1 in self.points :
              for p2 in other.points :
                  totdist += p1.distance(p2)
          average = totdist/(len(self.points)*len(other.points))
          return average
      def variability(self):
          totDist = 0.0
          for p in self.points :
              totDist += (p.distance(self.centroid))**2
          return totDist
      def update (self, points) :
          """update the oldcentroid and returns the change between one iteration """
          oldcentroid = self.centroid 
          self.points = points 
          #make sure there are actual points in a cluster 
          if(len(points)>0):
              self.centroid = self.computeCentroid()
              return oldcentroid.distance(self.centroid)
          else :
              return 0.0 
      def members(self) :
          for p in self.points :
              yield p
      def isIn(self, name):
          """trying to find is a point is in a cluster """
          for p in self.points :
              if p.getName() == name :
                  return True 
          return False 
      def toStr(self):
         result = ''
         for p in self.points :
             result = result + p.toStr() + ','
         return result[:-2]
      
      def getCentroid(self):
         return self.centroid
      def computeCentroid(self):
         vals = pylab.array([0.0]*self.points[0].dimensionality())
         for p in self.points :
             vals += p.getFeatures()
         centroid = Point('centroid', vals/float(len(self.points)))
         return centroid
      def __str__(self):
         name = []
         for p in self.points :
             name.append(p.getName())
         name.sort()
         result = 'Cluster with centroid' + str(self.centroid.getFeatures())+ 'contains:\n'
##         for e in name :
##             result = result + e + ', '
         return result[:-2]

## ## clusterSet is used to hierachical clustering         
##class ClusterSet(object) :
##     """set of cluster"""
##     def __init__(self,pointType):
##         self.members = []
##     def add(self, c):
##         """add one cluster in the list"""
##         if c in self.members :
##             raise ValueError
##         self.members.append(c)
##     def getClusters(self):
##         return self.members[:]
##     def mergeClusters(self, c1, c2):
##         """this will merge two clusters , by appending its members in a list and instantiate using Cluster class"""
##         points = [] 
##         for p in c1.members() :
##             points.append(p)
##         for p in c2.members() :
##             points.append(p)
##         newC = Cluster(points , type(p))
##         self.members.remove(c1)
##         self.members.remove(c2)
##         return newC 
##     def findClosest(self, metric):
##         """find the closest  pair of clusters and return a tuple of thoses 2 clusters"""
##         minDistance = metric (self.members[0],self.members[1])
##         toMerge = (self.members[0],self.members[1])
##         for c1 in self.members :
##             for c2 in self.members :
##                 if c1 == c2 :
##                     continue 
##                 if metric (c1,c2) < minDistance :
##                     minDistance = metric (c1, c2)
##                     toMerge = (c1, c2)
##         return toMerge
##     def MergeOne(self, metric, toPrint = False ):
##         """merge 2 cluster using findClosest"""
##         if len(self.members ) == 1 :
##             return None 
##         if len(self.members)  == 2 :
##             return mergeClusters(self.members[0],self.members[1])
##         ##otherwise find the closest pair 
##         toMerge = findClosest(metric) 
##         if toPrint :
##             print ('merged')
##             print (' '+ str(toMerge[0]))
##             print ('with')
##             print (' '+str(toMerge[1]))
##         self.mergeCluster(toMerge[0],toMerge[1])
##         ##return the merged 2 clusters 
##     def mergeN(self, metric, numClusters = 1, history = [], toPrint = False): 
##          assert numClusters >=1 
##          while len(self.members)> numClusters :
##              merged = self.MergeOne(metric, toPrint)
##              history.append(merged)
##          return history 
##     def numClusters(self):
##          return len(self.members) + 1
##     def __str__(self) :
##          result = ''
##          for c in self.members :
##              result = result + str(c) + '\n'
##          return result 


## k means 
def kmeans(points, k, verbose = False) :
    #first step : randomly choose k points 
    initialCentroids = random.sample(points, k)
    clusters = []
    #assign each of those points to its own cluster 
    for p in initialCentroids :
        clusters.append(Cluster([p]))
    converged = False
    numIter = 0
    while not converged :
        #creat a list containing k empty lists 
        newClusters = []
        for i in range (k):
            newClusters.append([])
        for p in points :
            #find the centroid closest to p ,which is a point 
            smallestDistance = p.distance(clusters[0].getCentroid())
            index = 0 
            for i in range(1,k) :
                distance = p.distance(clusters[i].getCentroid())
                if distance < smallestDistance :
                    smallestDistance = distance
                    index = i 
            ## add p to the list of points for appropriate cluster 
            newClusters[index].append(p)
        for c in newClusters :
            if (len(c) == 0):
                raise ValueError('Empty Cluster')    
        ## now update the cluster and calculate change
        converged = True
        for i in range(k):
            if clusters[i].update(newClusters[i]) > 0.0 :
                converged = False 
                clusters[i].addlabel(k+1)
        numIter +=1
   
        if verbose :
              print ('Number of iterations =' + str(numIter))
              for c in clusters :
                  print(c)
              print('')     
    return clusters     
##find the best k values 
def dissimilarity(clusters):
    totDist = 0.0 
    for c in clusters :
        totDist += c.variability()
    return totDist

def tryKmeans(points, numClusters, numTrials, verbose = False):
    """call k means multiple times and return the result with least dissimilarity"""
    best = kmeans(points, numClusters, verbose = False)
    minDissimilarity = dissimilarity(best)
    trial = 1 
    while trial < numTrials :
        try :
            clusters = kmeans(points, numClusters, verbose)
        except ValueError:
            continue
        currDissimilarity = dissimilarity(clusters)
        if currDissimilarity < minDissimilarity:
            best = clusters
            minDissimilarity = currDissimilarity
        trial += 1
    return best 



## generate some randomly distributed points for testing 
def genDistribution (xMean, xSD, yMean, ySD, n, namePrefix) :
    samples = []
    for s in range(n) :
        x = random.gauss(xMean, xSD)
        y = random.gauss(yMean, ySD)
        samples.append(Point(namePrefix+str(s),[x,y]))
    return samples
def plotSamples(samples, marker):
    xVals, yVals =[], []
    for s in samples :
        x = s.getFeatures()[0]
        y = s.getFeatures()[1]
        pylab.annotate(s.getName(),xy = (x,y), xytext = (x+0.13, y-0.07), fontsize = 'x-large')
        xVals.append(x)
        yVals.append(y)
    pylab.plot(xVals, yVals, marker)
def contrivedTest(numTrials, k, verbose = False):
    xMean = 3 
    xSD = 1 
    yMean = 5
    ySD = 1 
    n = 10 
    d1samples = genDistribution(xMean, xSD, yMean, ySD, n, 'A')
    #plotSamples(d1samples,'k^')
    d2samples = genDistribution(xMean+3, xSD, yMean+1, ySD, n, 'B')
    #plotSamples(d2samples,'ko')
    points = d1samples + d2samples
    clusters = tryKmeans(points, k, numTrials, verbose)
    #try to plot points in different cluster using different color 
    marker = ['r^','bo']
    i = 0 
    for c in clusters :
        plotSamples(c.points,marker[i])
        i += 1

    pylab.show()
    print('Final result')
    for c in clusters :
        print(c)
def readGazeData(fName):
    samples = []
    i = 0
    with open(fName,'r') as f :
        try :
            for line in f :
                contents = line.split(',')
                x = contents[0]
                y = contents[1]
                
                ##only read the first 2 columns of data ,ignore time stamp for now 
                samples.append(Point('',[float(x),float(y)]))
                i = i + 1
                
        except ValueError :
            pass
    return samples
def Test(fileName = None, keyboard = False) :
    points = readGazeData('combined_calibration_log.txt')
    clusters = tryKmeans(points, 4, 4, False)
    ## give each point in cluster a label [A, B, C,D]
    label = ['A', 'B', 'C', 'D']
    centroids = []
    result_x, result_y =[], []
    marker = ['ro','bo','ko','go']
    i = 0
    #print('Final result')
    for c in clusters :
        plotSamples(c.points,marker[i])
        i+=1
        centroids.append(c.getCentroid().getFeatures().tolist())
    for q in centroids :
        result_x.append(q[0])
        result_y.append(q[1])
    avg_x = sum(result_x)/4
    avg_y = sum(result_y)/4
    centroid_of_centroid =[avg_x,avg_y]
    sorted_centroids = sorted(centroids, key = lambda k: k[0])
    #print(sorted_centroids)
    #print centroids to a file
    f = open("centroids.txt",'w')
    if keyboard == False :
        for item in centroids:
            if item[0] < avg_x and item[1] > avg_y: 
               f.write("%s\n"%item)
            elif item[0] > avg_x and item[1] > avg_y:
               f.write("%s\n"%item)
            elif item[0] < avg_x and item[1] < avg_y:
               f.write("%s\n"%item)
            elif item[0] > avg_x and item[1] < avg_y:
               f.write("%s\n"%item)
    else :
        for item in sorted_centroids:
            f.write("%s\n"%item)
        
    k = 0
    
    for c in clusters :
        index = sorted_centroids.index(c.getCentroid().getFeatures().tolist())
        for p in c.points :
                     p.label = label[index]
    #print(clusters[0].points[0])
    #print(clusters[1].points[0])
    #print(clusters[2].points[0])
    #print(clusters[3].points[0])
    #pylab.show()
    return clusters

def getGazedata(clusters):
    data ={}  ##defined as dictionary 
    data['selection'], data['x_coor'], data['y_coor'] = [], [], []
    for c in clusters :
        for p in c.points:
               data['selection'].append(p.label)
               data['x_coor'].append(p.getFeatures()[0])
               data['y_coor'].append(p.getFeatures()[1])
    return data

def Test_classify(n) :
    clusters = Test(1, 4, False)
    training = getGazedata(clusters)
    print(training['selection'][n]+ ' x_coor is' + str(training['x_coor'][n])+' y_coor is' + str(training['y_coor'][n]))

if __name__ == '__main__':
    Test()





