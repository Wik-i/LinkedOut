import re
import pandas as pd
import sys, os
import numpy as np
import nltk
import operator
import math
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

class Extractor():
        def __init__(self, filename):
                #self.softskills=self.load_skills('web_developer/softskills.txt')
                #self.hardskills=self.load_skills('web_developer/hardskills.txt')
                self.softskills=self.load_skills('match/softskills.txt')
                self.hardskills=self.load_skills('match/softskills.txt')
                
                self.table=list()
                self.readfile=filename
                #self.outFile="Extracted_keywords.csv"
                self.detaillist=list()
                self.simlist=list()
                self.joblist = ['web_developer', 'game_designer']

                self.jb_distribution = list()
                for j in self.joblist:
                        self.jb_distribution.append(self.build_ngram_distribution_txt('match/'+j+'_description.txt'))

                self.cv_distribution=self.build_ngram_distribution_pdf()

        def convert(self, fname, pages=None):
                if not pages:
                        pagenums = set()
                else:
                        pagenums = set(pages)

                output = StringIO()
                manager = PDFResourceManager()
                converter = TextConverter(manager, output, laparams=LAParams())
                interpreter = PDFPageInterpreter(manager, converter)

                infile = open(fname, 'rb')
                for page in PDFPage.get_pages(infile, pagenums):
                        interpreter.process_page(page)
                oname = fname.replace(".pdf", ".txt")
                infile.close()
                converter.close()
                text = output.getvalue()
                text_file = open(oname, "w" ,encoding="utf-8")
                text_file.write(text)
                output.close
                text_file.close()
                return text 
                        
        def load_skills(self,filename):
                f=open(filename,'r')
                skills=[]
                for line in f:
                        #去除标点符号和大写
                        skills.append(self.clean_phrase(line)) 
                f.close()
                return list(set(skills))  #去除重复元素


        def build_ngram_distribution_pdf(self):
                n_s=[1,2,3] #mono-, bi-, and tri-grams
                dist={}
                for n in n_s:
                        dist.update(self.parse_pdffile(n))
                return dist

        def build_ngram_distribution_txt(self,filename):
                n_s=[1,2,3] #mono-, bi-, and tri-grams
                dist={}
                for n in n_s:
                        dist.update(self.parse_txtfile(filename,n))
                return dist

        def parse_pdffile(self,n):
                self.convert(self.readfile)
                oname = self.readfile.replace(".pdf", ".txt")
                f=open(oname,'r', encoding='utf-8')
                results={}
                for line in f:
                        words=self.clean_phrase(line).split(" ")
                        ngrams=self.ngrams(words,n)
                        for tup in ngrams:
                                phrase=" ".join(tup)
                                if phrase in results.keys():
                                        results[phrase]+=1
                                else:
                                        results[phrase]=1
                return results
        
        def parse_txtfile(self,filename,n):
                f=open(filename,'r', encoding='utf-8')
                results={}
                for line in f:
                        words=self.clean_phrase(line).split(" ")
                        ngrams=self.ngrams(words,n)
                        for tup in ngrams:
                                phrase=" ".join(tup)
                                if phrase in results.keys():
                                        results[phrase]+=1
                                else:
                                        results[phrase]=1
                return results

        
        def clean_phrase(self,line):
                return re.sub(r'[^\w\s]','',line.replace('\n','').replace('\t','').lower())             
                


        def ngrams(self,input_list, n):
                return list(zip(*[input_list[i:] for i in range(n)]))

        def measure1(self,v1,v2):
                return v1-v2

        def measure2(self,v1,v2):
                return max(v1-v2,0)

        def measure3(self,v1,v2):
                sumxx, sumxy, sumyy = 0, 0, 0
                for i in range(len(v1)):
                        x = v1[i]; y = v2[i]
                        sumxx += x*x
                        sumyy += y*y
                        sumxy += x*y
                if sumxx * sumyy != 0:
                        return sumxy/math.sqrt(sumxx*sumyy)
                else:
                        return 0
        

        def sendToFile(self, i):
                outfile = self.joblist[i] + "_Extracted_Keywords.csv"
                try:
                        os.remove(outfile)
                except OSError:
                        pass
                df=pd.DataFrame(self.table[i],columns=['type','skill','job','cv','m1','m2'])
                df_sorted=df.sort_values(by=['job','cv'], ascending=[False,False])
                df_sorted.to_csv(outfile, columns=['type','skill','job','cv'],index=False)

        def getMeasures(self, i):
                n_rows=len(self.table[i])          
                v1=[self.table[i][m1][4] for m1 in range(n_rows)]
                v2=[self.table[i][m2][5] for m2 in range(n_rows)]
                #print("Measure 1: ",str(sum(v1)))
                #print("Measure 2: ",str(sum(v2)))
                
                v1=[self.table[i][jb][2] for jb in range(n_rows)]
                v2=[self.table[i][cv][3] for cv in range(n_rows)]
                #print("Measure 3 (cosine sim): ",str(self.measure3(v1,v2)))
                
                sim = 0
                for type in ['hard','soft','general']:
                        v1=[self.table[i][jb][2] for jb in range(n_rows) if self.table[i][jb][0]==type]
                        v2=[self.table[i][cv][3] for cv in range(n_rows) if self.table[i][cv][0]==type]
                        #print("Cosine similarity for "+type+" skills: "+str(self.measure3(v1,v2)))  
                        self.detaillist.append(self.joblist[i]+": "+type+"_skills cosine similarity"+str(self.measure3(v1,v2)))
                        if type=='hard':
                                sim += 0.5*self.measure3(v1,v2)
                        elif type=='soft':
                                sim += 0.3*self.measure3(v1,v2)
                        elif type=='general':
                                sim += 0.2*self.measure3(v1,v2)
                self.simlist.append(sim)


        def makeTable(self, i):            
                #I am interested in verbs, nouns, adverbs, and adjectives
                parts_of_speech=['CD','JJ','JJR','JJS','MD','NN','NNS','NNP','NNPS','RB','RBR','RBS','VB','VBD','VBG','VBN','VBP','VBZ']
                graylist=["you", "will"]
                tmp_table=[]
                #查找softskills和hardskills中的哪些在职业描述和简历中存在
                
                for skill in self.hardskills:
                        if skill in self.jb_distribution[i]:
                                count_jb=self.jb_distribution[i][skill]
                                if skill in self.cv_distribution:
                                        count_cv=self.cv_distribution[skill]
                                else:
                                        count_cv=0
                                m1=self.measure1(count_jb,count_cv)
                                m2=self.measure2(count_jb,count_cv)
                                tmp_table.append(['hard',skill,count_jb,count_cv,m1,m2])

                for skill in self.softskills:
                        if skill in self.jb_distribution[i]:
                                count_jb=self.jb_distribution[i][skill]
                                if skill in self.cv_distribution:
                                        count_cv=self.cv_distribution[skill]
                                else:
                                        count_cv=0
                                m1=self.measure1(count_jb,count_cv)
                                m2=self.measure2(count_jb,count_cv)
                                tmp_table.append(['soft',skill,count_jb,count_cv,m1,m2])
                                                

                #排序职业描述中最常出现的单词

                general_language = sorted(self.jb_distribution[i].items(), key=operator.itemgetter(1), reverse=True)
                for tuple in general_language:
                        skill = tuple[0]
                        if skill in self.hardskills or skill in self.softskills or skill in graylist:
                                continue
                        count_jb = tuple[1]
                        tokens=nltk.word_tokenize(skill) #分词，拆解长句子
                        parts=nltk.pos_tag(tokens) #标注词语对应词性
                        if all([parts[i][1]in parts_of_speech for i in range(len(parts))]):
                                if skill in self.cv_distribution:
                                        count_cv=self.cv_distribution[skill]
                                else:
                                        count_cv=0
                                m1=self.measure1(count_jb,count_cv)
                                m2=self.measure2(count_jb,count_cv)
                                tmp_table.append(['general',skill,count_jb,count_cv,m1,m2])
                self.table.append(tmp_table)
        
        def match(self):
                for i in range(len(self.joblist)):
                        self.makeTable(i)
                        #self.sendToFile(i)
                        self.getMeasures(i)
                #print(K.simlist)
                sim = sorted(self.simlist, reverse=True)
                #for i in range(2):
                #        print(self.joblist[i] + " matching rate: " + str(sim[i]))
                return sim
        


"""
def main():
        K=Extractor('lylresume.pdf')
        K.match()



if __name__ == "__main__":
    main()
"""         
