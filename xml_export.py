import xml.etree.ElementTree as ET
from datetime import datetime

#build tree

def create_quiz(headerelements, fragendicts):
    """baut fragen4xml aus fragendicts
    Parameter: headerelements = List[String], fragendicts = List[Dict]
        Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
    Return: quiz = xmltree
    """
    quiz=ET.Element('quiz')
    for textelement in headerelements:
        quiz.append(create_question_header(textelement))
    for fragendict in fragendicts:
        quiz.append(create_question_main(fragendict))
    return quiz

def create_question_header(headerelement):
    """baut header für quiz
    Parameter: headerelement = String
    Return: question = ET.Element
    """
    question=ET.Element('question', type='category')
    question.append(create_category_header(headerelement))
    return question

def create_category_header(headerelement):
    """baut Kategorie für Quizheader
    Parameter: headerelement = String
    Return: category = ET.Element
    """
    category=ET.Element('category')
    category.append(create_text_header(headerelement))
    return category

def create_text_header(headerelement):
    """baut text für Kategorieheader
    Parameter: headerelement = String
    """
    text = ET.Element('text')
    text.text=headerelement
    return text

def create_question_main(fragendict):
    """Baut die Frage für XML aus fragendict
    Parameter: headerelements = List[String], fragendicts = List[Dict]
        Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
    Return: question = ET.Element
    """
    question=ET.Element('question', type='multichoice')
    fragentitel=fragendict.get('Fragentitel')
    question.append(create_name_main_kh(fragentitel))
    #fragen
    questiontext=ET.Element('questiontext', format='html')
    text=ET.Element('text')
    text.text=fragendict.get('Frage')
    questiontext.append(text)
    question.append(questiontext)
    #settings
    defaultgrade=ET.Element('defaultgrade')
    defaultgrade.text='%s'%(len(fragendict.get('Antworten')))
    question.append(defaultgrade)
    singleans=ET.Element('single')
    singleans.text='false'
    question.append(singleans)
    shuffleanswers=ET.Element('shuffleanswers')
    shuffleanswers.text='true'
    question.append(shuffleanswers)
    answernumbering=ET.Element('answernumbering')
    answernumbering.text='none'
    question.append(answernumbering)
    #feedback
    (correctfeedback,partiallycorrectfeedback,incorrectfeedback)=create_feedback_main()
    question.append(correctfeedback)
    question.append(partiallycorrectfeedback)
    question.append(incorrectfeedback)
    #antworten           
    question=create_answer_main(question, fragendict)
    return question

def create_name_main_kh(fragentitel):
    """baut fragentitel in xml
    Parameter: fragentitel = String
    Return: name = ET.Element
    """
    name=ET.Element('name')
    name.append(create_text_main_kh(fragentitel))
    return name

def create_text_main_kh(fragentitel):
    """baut fragentitel als text in xml ein
    Parameter: fragentitel = String
    Return: text = ET.Element
    """
    text=ET.Element('text')
    text.text=fragentitel
    return text

def create_feedback_main():
    """Baut Feedback in xml ein
    return correctfeedback, partiallycorrectfeedback, incorrectfeedback = ET.Element
    """
    correctfeedback=ET.Element('correctfeedback', format='html')
    text=ET.Element('text')
    text.text='Die Antwort ist richtig'
    correctfeedback.append(text)
    
    partiallycorrectfeedback=ET.Element('partiallycorrrectfeedback', format='html')
    text=ET.Element('text')
    text.text='Die Antwort ist teilweise richtig'
    partiallycorrectfeedback.append(text)
    
    incorrectfeedback=ET.Element('incorrectfeedback', format='html')
    text=ET.Element('text')
    text.text='Die Antwort ist falsch'
    incorrectfeedback.append(text)
    return correctfeedback, partiallycorrectfeedback, incorrectfeedback

def create_answer_main(question, fragendict):
    """
    Baut Antwort für Frage in xml
    Parameter: question = ET.Element, fragendict = Dict 
            Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
    Return: question = ET.Element
    """
    rcounter=0
    for antwort in fragendict.get('Antworten'):
        if fragendict.get('Antworten').get(antwort)=='right':
            rcounter+=1
    if rcounter == 0:
        pointsright=0
    else:
        pointsright=100/rcounter
    if (len(fragendict.get('Antworten'))-rcounter) != 0:
        pointswrong=100/((len(fragendict.get('Antworten'))-rcounter))
    else: 
        pointswrong=0
    for antwort in fragendict.get('Antworten'):
        if fragendict.get('Antworten').get(antwort)=='right':
            answer=ET.Element('answer', format='html', fraction='%s'%pointsright)
        else:
            answer=ET.Element('answer', format='html', fraction='-%s'%pointswrong)
        text=ET.Element('text')
        text.text=('%s'%(antwort))
        answer.append(text)
        question.append(answer)
    return question

def create_file(fragendicts):
    """Baut XML-File auf für fragen von fragendicts
    Parameter: fragendicts = List[Dict]
            Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}    
    """
    #header
    dt=datetime.now()
    dtstring=dt.strftime('%Y.%m.%d_%H:%M')
    coursetop='$course$/Krankheitslehrefragen(%s)'%dtstring
    ba_mit_fragen=coursetop
    headerelements=[coursetop, ba_mit_fragen]
    #main
    quiz=create_quiz(headerelements, fragendicts)
    data=ET.tostring(quiz)
    exportfile=open('Quizexport.xml', 'wb')
    exportfile.write(data)
    exportfile.close()

#export to File