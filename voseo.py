# -*- coding: utf-8 -*-
#configuration variables
#Edit cap
#This feature caps the number of edits performed by this program. Once the limit has been reached, the program will stop editing. Set to None to disable cap, 0 to disable editing, or a number to set the cap.
editcap=None
#To minimize edit traffic, you can set time limits on the editing made by this program.
#Pywikibot has its own time limiting system, but you can enable this as an additional edit-limiting measure or when some additional randomness is desired.
#Set to True to enable the time limiter.
timelimit_enable=False
#The minimum time to wait between edits.
timelimit_min=0
#The maximum time to wait between edits.
timelimit_max=10
#Set to True to stop editing if your talk page is edited.
talkstop=True
#End of configuration, source follows.
import pywikibot
from pywikibot import pagegenerators
import traceback
if timelimit_enable:
    import random
    import time

en=pywikibot.Site('en','wiktionary')
es=pywikibot.Site('es','wiktionary')
rlgen = pagegenerators.CategorizedPageGenerator(pywikibot.Category(en,'Category:Spanish verbs having voseo red links in their conjugation table'))
rlargen = pagegenerators.CategorizedPageGenerator(pywikibot.Category(en,'Category:Spanish verbs having voseo red links in their conjugation table (regular -ar verbs)'))
rlcargen = pagegenerators.CategorizedPageGenerator(pywikibot.Category(en,'Category:Spanish verbs having voseo red links in their conjugation table (-car)'))
rlgargen = pagegenerators.CategorizedPageGenerator(pywikibot.Category(en,'Category:Spanish verbs having voseo red links in their conjugation table (-gar)'))
badgen = pagegenerators.CategorizedPageGenerator(pywikibot.Category(en,'Category:Spanish terms with red links in their inflection tables'))
argen = pagegenerators.CategorizedPageGenerator(pywikibot.Category(en,'Category:Spanish verbs ending in -ar'))
ergen = pagegenerators.CategorizedPageGenerator(pywikibot.Category(en,'Category:Spanish verbs ending in -er'))
irgen = pagegenerators.CategorizedPageGenerator(pywikibot.Category(en,'Category:Spanish verbs ending in -ir'))
editcount=0
def stripreflexives(infinitive):
    "Strips reflexive and object pronouns from an infinitive."
    end = infinitive[len(infinitive)-2:]
    if end.lower() in ('me','te','le','se','nos','os','les','lo','la','los','las'):
        return infinitive[:len(infinitive)-2]
    else:
        return infinitive

def get_ending(infinitive):
    "Get the ending of a Spanish infinitive (ar, er, or ir). Return None if unable to determine."
    #Handle reflexives.
    infinitive=stripreflexives(infinitive)
    end = infinitive[len(infinitive)-2:]
    if end in ('ar','er','ir'):
        return end
    else:
        return None

def get_stem(infinitive):
    "Get the stem of a Spanish infinitive (I.E. habl, com, viv). Raise ValueError if unable to determine."
    infinitive=stripreflexives(infinitive)
    if infinitive[len(infinitive)-2:] in ('ar','er','ir'):
        return infinitive[:-2]
    raise ValueError
def get_regular_voseo(infinitive,ending='',mood='indicative'):
    "Gets the regular vos form of a verb (what the form would be if the verb were regular). Does not account for irregularities, but there are few in this form. Still recommended to check the result for validity somehow. Takes an infinitive, an ending, and a mood (\'indicative\', \'imperative\', or \'subjunctive\') will attempt to auto-determine ending if not provided, and defaults to indicative mood. Raises ValueError if unable to determine."
    if ending == '':
        ending = get_ending(infinitive)
    if ending == None:
        raise ValueError("Can't determine ending of " + infinitive)
    if stripreflexives(infinitive)[len(stripreflexives(infinitive))-3:] == 'car' and mood == 'subjunctive':
        return get_stem(infinitive)[:-1]+"qués"
    if stripreflexives(infinitive)[len(stripreflexives(infinitive))-3:] == 'gar' and mood == 'subjunctive':
        return get_stem(infinitive)[:-1]+"gués"
    if stripreflexives(infinitive)[len(stripreflexives(infinitive))-3:] == 'zar' and mood == 'subjunctive':
        return get_stem(infinitive)[:-1]+"cés"
    if ending == 'ar':
        if mood == 'indicative':
            return get_stem(infinitive)+"ás"
        elif mood == 'imperative':
            return get_stem(infinitive)+"á"
        elif mood == 'subjunctive':
            return get_stem(infinitive)+"és"
        else:
            raise ValueError
    elif ending == 'er':
        if mood == 'indicative':
            return get_stem(infinitive)+"és"
        elif mood == 'imperative':
            return get_stem(infinitive)+"é"
        elif mood == 'subjunctive':
            return get_stem(infinitive)+"ás"
        else:
            raise ValueError
    elif ending == 'ir':
        if mood == 'indicative':
            return get_stem(infinitive)+"ís"
        elif mood == 'imperative':
            return get_stem(infinitive)+"í"
        elif mood == 'subjunctive':
            return get_stem(infinitive)+"ás"
        else:
            raise ValueError

    else:
        raise ValueError

def page_exists(site,name):
    "Checks if a page exists on a pywikibot.Site, returns True/False."
    return pywikibot.Page(site,name).exists()

def is_hole(infinitive,mood='indicative',algo='both',checkspanish=True):
    "Checks if a verb matches the voseo hole pattern (does not exist in English Wiktionary, but does in Spanish). Takes an infinitive, a mood (indicative, imperative, subjunctive, or all), and a checking algorithm (\'fast\', \'slow\' or \'both\'). Defaults to indicative mood and both checking algorithms, in order of speed. Pass \'checkspanish=False\' to skip Spanish wiktionary check. Returns True/False if a single mood is passed, or a  list of moods where a hole exists if all is passed."
    if mood != 'all':
        if algo == 'fast':
            return page_exists(en,get_regular_voseo(infinitive,mood=mood)) == False and (checkspanish==False or '|p=2sv' in pywikibot.Page(es,get_regular_voseo(infinitive,mood=mood)).text or '|vos|' in pywikibot.Page(es,get_regular_voseo(infinitive,mood=mood)).text or '|p=vos' in pywikibot.Page(es,get_regular_voseo(infinitive,mood=mood)).text)
        elif algo == 'slow':
            return 'voseo=y' not in pywikibot.Page(en,get_regular_voseo(infinitive,mood=mood)).text and infinitive in pywikibot.Page(en,get_regular_voseo(infinitive,mood=mood)).text and (checkspanish==False or '|p=2sv' in pywikibot.Page(es,get_regular_voseo(infinitive,mood=mood)).text or '|vos|' in pywikibot.Page(es,get_regular_voseo(infinitive,mood=mood)).text or '|p=vos' in pywikibot.Page(es,get_regular_voseo(infinitive,mood=mood)).text)
        elif algo == 'both':
            return is_hole(infinitive=infinitive,mood=mood,algo='fast',checkspanish=checkspanish) or is_hole(infinitive=infinitive,mood=mood,algo='slow',checkspanish=checkspanish)
        else:
            raise ValueError
    else:
        res=[]
        for m in ('indicative','imperative','subjunctive'):
            if is_hole(infinitive,mood=m,algo=algo,checkspanish=checkspanish):
                res.append(m)
        return res
def generate_vostext(infinitive,vosform=None,ending=None,mood='indicative',header=True):
    "Generates the text for a voseo definition."
    if vosform == None:
        vosform=get_regular_voseo(infinitive,mood=mood)
    if ending == None:
        ending=get_ending(infinitive)
    text=''
    if header:
        text += "==Spanish==\n\n===Verb===\n{{head|es|verb form}}\n"
    text += "# {{es-verb form of|ending=" + ending + "|mood=" + mood
    if mood == 'imperative':
        text+='|sense=affirmative'
    text += "|tense=present|pers=2|voseo=yes|formal=no|number=singular|" + infinitive + "|region=Latin America}}\n"
    return text
def fix_hole(infinitive,vosform=None,ending=None,mood='indicative',force=False):
    "Patch a voseo hole. Takes an infinitive, and optionally the vosform, ending, and mood (\'indicative\', \'imperative\' or \'subjunctive\') otherwise we autodetect and default to \'indicative\'. We check if a hole exists before making changes, disable by passing Force=True. Returns True on success, false on error."
    global editcount,editcap
    if editcap != None and editcount >= editcap:
        return False
    if is_hole(infinitive,mood=mood) == False and force == False:
        print("Can't fix hole since it doesn't exist, pass Force=True to override.")
        return False
    global timelimit_enable
    if timelimit_enable:
        global timelimit_min,timelimit_max
        wait=random.randint(timelimit_min,timelimit_max)
        print("Time limiter activated, sleeping for",wait,"seconds.")
        time.sleep(wait)

    if vosform == None:
        vosform=get_regular_voseo(infinitive,mood=mood)
    if page_exists(en,vosform):
        vospage=pywikibot.Page(en,vosform)
        voslist=vospage.text.split('\n')
        sindex=None
        for r in range(len(voslist)):
            if '{{es-verb-form}}' in voslist[r].lower():
                sindex=r
                break
        if sindex == None:
            for r in range(len(voslist)):
                if "[[es:" in voslist[r]:
                    voslist.insert(r-1,generate_vostext(infinitive=infinitive,mood=mood,vosform=vosform))
                    vospage.text='\n'.join(voslist).replace('\n\n\n','\n\n')
                    vospage.save("Added Spanish section.")
                    editcount+=1
                    return True
        else:
            i=sindex
            #Find beginning of definitions.
            while voslist[i].startswith('#') == False:
                i+=1
                continue
            #Find last definition.
            while voslist[i].startswith('#'):
                i+=1
                continue
            voslist.insert(i,generate_vostext(infinitive=infinitive,mood=mood,vosform=vosform,header=False))
            vospage.text='\n'.join(voslist).replace('\n\n\n','\n\n')
            vospage.save("Added voseo.")
            editcount+=1
            return True
    if ending == None:
        ending=get_ending(infinitive)
    try:
        page=pywikibot.Page(en,vosform)
        page.text=generate_vostext(infinitive=infinitive,vosform=vosform,mood=mood,header=True)
        page.save("\n")
    except:
        print("Exception caught, can't fix hole - traceback follows:",traceback.format_exc())
        return False
    else:
        editcount+=1
        return True

def generate_csv(generator=rlgen):
    "Generate a csv file of regular voseo forms from a pagegenerator."
    import csv
    fout=open('voseo.csv','w')
    writer=csv.writer(fout)
    writer.writerow(('infinitivo','indicativo','imperativo afirmativo','subjunctivo'))
    for i in generator:
        try:
            if i.title()[len(i.title())-2:] in ('me','te','se','nos','os'):
                continue
            writer.writerow((i.title(),get_regular_voseo(i.title(),mood='indicative'),get_regular_voseo(i.title(),mood='imperative'),get_regular_voseo(i.title(),mood='subjunctive')))
        except ValueError:
            continue
    fout.close()
def get_holes():
    "Checks the English Wiktionary's ar, er, and ir verbs for their regular vos forms. If none is found for a verb, but an entry for that form exists in the Spanish wiktionary, it is returned."
    count=0
    global talkstop
    if talkstop:
        talkrev=pywikibot.Page(en,"user_talk:" + en.username()).latestRevision()
    print("Searching known Voseo redlinks...")
    for rl in rlgen:
        if talkstop and pywikibot.Page(en,"user_talk:" + en.username()).latestRevision() != talkrev:
            print("Talk page edited, stopping...")
            break
        count+=1
        try:
            for m in is_hole(rl.title(),mood='all'):
                fix_hole(rl.title(),mood=m)
        except ValueError:
            print("Caught value error in",rl.title(),".")
            continue
        if count%25 == 0:
            print(count,"known Voseo redlinks scanned so far,", editcount, "edits so far.")
    print ("A total of", count, "known Voseo redlinks scanned. Searching Spanish terms known to have redlinks...")
    for rl in badgen:
        if talkstop and pywikibot.Page(en,"user_talk:" + en.username()).latestRevision() != talkrev:
            print("Talk page edited, stopping...")
            break
        count+=1
        try:
            for m in is_hole(rl.title(),mood='all'):
                fix_hole(rl.title(),mood=m)
        except ValueError:
            print("Caught value error in",rl.title(),".")
            continue
        if count%25 == 0:
            print(count,"known redlinks scanned so far,", editcount, "edits so far.")
    print("Known redlinks scanned. " + str(editcount) + " edits performed. Starting full scan, starting with ar...")
    count=0
    for a in argen:
        if talkstop and pywikibot.Page(en,"user_talk:" + en.username()).latestRevision() != talkrev:
            print("Talk page edited, stopping...")
            break
        count+=1
        try:
            for m in is_hole(a.title(),mood='all'):
                fix_hole(a.title(),mood=m)
        except ValueError:
            continue
        if count%100 == 0:
            print(count,"ar verbs checked so far.", editcount, "edits so far.")
    print ("A total of", count, "ar verbs checked. Searching er...")
    count=0
    for e in ergen:
        if talkstop and pywikibot.Page(en,"user_talk:" + en.username()).latestRevision() != talkrev:
            print("Talk page edited, stopping...")
            break
        count+=1
        try:
            for m in is_hole(e.title(),mood='all'):
                fix_hole(e.title(),mood=m)
        except ValueError:
            continue
        if count%100 == 0:
            print(count,"er verbs checked so far.", editcount, "edits so far.")

    print ("A total of", count, "er verbs checked. Searching er...")
    count=0
    for i in irgen:
        if talkstop and pywikibot.Page(en,"user_talk:" + en.username()).latestRevision() != talkrev:
            print("Talk page edited, stopping...")
            break
        count+=1
        try:
            for m in is_hole(i.title(),mood='all'):
                fix_hole(i.title(),mood=m)
        except ValueError:
            continue
        if count%100 == 0:
            print(count,"er verbs checked so far.", editcount, "edits made so far.")
    print ("A total of", count, "ir verbs checked. Scan complete.",editcount,"edits performed.")

if __name__ == '__main__': get_holes()
