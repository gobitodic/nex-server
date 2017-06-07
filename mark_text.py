import sqlite3
import dataset
import os

def mark_text (text_output,tools):
    #text="Washington (dpa) - Donald Trumps Sprecher Sean Spicer will die viel kritisierte Äußerung des US-Präsidenten nicht zurücknehmen, wonach Medien die Feinde des Volkes seien. Der Präsident habe eine gesunden Respekt vor den Medien, sagte Spicer am Dienstag. «Wir haben eine freie Presse», fügte er hinzu, aber einige Medien würden absichtlich unkorrekt über Trumps Leistungen berichten. Der US-Präsident hatte am vergangenen Freitag getwittert, die «Fake News Medien» seien nicht sein Feind, sondern Feind des amerikanischen Volkes. Nach Ansicht vieler Kritiker auch von republikanischer Seite überschritt Trump damit eine Linie."
    output_object=[]
    # path_original = "/Users/alex/nex-analysis-server/hug-minimal-server"
    # path = "/Users/alex/nex-analysis"
    # os.chdir(path)
    db='sqlite:///nex-analysis.db'
    database = dataset.connect(db)
    # os.chdir(path_original)
    text=text_output["text"]
    dpa_id=text_output["dpa_id"]
    dpa_id_id=list(database.query("""
        select 
        rowid
        from dpa_text  where 
        dpa_id=:dpa_id
        """,dpa_id=dpa_id))[0]["rowid"]
    for tool in tools:
        
        tool_id=list(database.query("""
            select 
            rowid
            from tools where 
            tool=:tool
            """,tool=tool))[0]["rowid"]
        entities=list(database.query("""
            select 
            start,end,surface, confidence, entity_id 
            from found_entities  where 
            tool_id=:tool_id and dpa_id=:dpa_id_id
            order by start asc
            """,tool_id=tool_id,dpa_id_id=dpa_id_id))

        length=len(entities)
        #print(length)
        sum_confidence=0
        length_confidence=0
        word_count=len(text.split())
        #print(word_count)
        try:
            rate_entity=round(word_count/length,1)
        except ZeroDivisionError:
            rate_entity="ERROR"
        for entity in entities:
            try:
                sum_confidence=sum_confidence+float(entity["confidence"])
                
            except TypeError:
                length_confidence=length_confidence-1
            length_confidence=length_confidence+1
            entity_id=entity["entity_id"]
            information=list(database.query(
                """
                select 
                uri,label,labelfromsurface, extra 
                from entity  where 
                rowid=:entity_id
                """,entity_id=entity_id))[0]
            entity["uri"]=information["uri"]
            entity["label"]=information["label"]
            entity["labelfromsurface"]=information["labelfromsurface"]
            entity["extra"]=information["extra"]
        y=0
        text_list=[]
        for x in range(0,length):
            part=text[y:int(entities[x]["start"])]
            text_list.append({"status":"text","text":part})
            entity_element=text[int(entities[x]["start"]):int(entities[x]["end"])]
            if entities[x]["labelfromsurface"]==0:
                label= entities[x]["label"]
            else:
                label= "no label found"
            if tool == tools[0]:
                color= "yellow"
            elif tool == tools[1]:
                color = "lime"
            elif tool == tools[2]:
                color= "lightpink"
            elif tool == tools[3]:
                color= "PaleGoldenRod"
            else:
                color = "turquoise"
            try:
                confidence=round(entities[x]["confidence"],3)
            except TypeError:
                confidence = "No confidence found"
            text_list.append({
                "status":"entity",
                "text":entity_element,
                "uri":entities[x]["uri"],
                "confidence":confidence,
                "label":label,
                "color":color
                })
            y=entities[x]["end"]
        
        end=text[y:len(text)]
        text_list.append({"status":"text","text":end})


        try:
            avg_confidence=round(sum_confidence/length_confidence,3)
        except ZeroDivisionError:
            avg_confidence= "Error"
        #print(sum_confidence)
        #print(length_confidence)
        input={
            "tool":tool,
            "avg_confidence":avg_confidence,
            "length":length,
            "text_list":text_list,
            "rate_entity":rate_entity
            }
        output_object.append(input)           
    return(output_object)
        

