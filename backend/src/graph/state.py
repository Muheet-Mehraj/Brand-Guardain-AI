import operator
from typing import Annotated, List, Dict, Optional, Any, TypeDict


class ComplianceIssue(TypeDict):
    category : str
    description : str # Specific Detail of Violation
    severity : str #Critical Warning
    timestamp : Optional[str]


# define the global graph state 
#This defines the state that gets passed around in the agentic workflow
class   VideoAuditState(TypeDict):
    '''Defines the data schema for langgraph execution content
       Main Container : Holds all the information about the audit
    '''
# Input parameters
video_url : str
video_id : str

# ingestion and extraction of data
local_file_path : Optional[str]
video_metadata : Dict[str,Any] #Duration :15 ,"resolution" : "1080p"
transcript : Optional[str] # Fully extracted speech to text
ocr_text : List[str] 

# Analysis output
compliance_results : Annotated[List[ComplianceIssue], operator.add ]

#final deliverables:
final_status : str #pass | Fail
final_report : str #Markdown

# System Observablity