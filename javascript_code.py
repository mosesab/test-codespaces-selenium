
# JavaScript code to be executed
class JS_GoogleMeetBot(object):
	js_code = """googleMeetStart = false;

    function googleMeetCheck(){
    if(document.getElementsByClassName("AE8xFb OrqRRb GvcuGe goTdfd")[0] == undefined){
        temp = document.getElementsByClassName("VYBDae-Bz112c-LgbsSe VYBDae-Bz112c-LgbsSe-OWXEXe-SfQLQb-suEOdc hk9qKe  S5GDme gVYcob JsuyRc boDUxc")[1];
        if(temp != undefined){
            document.getElementsByClassName("VYBDae-Bz112c-LgbsSe VYBDae-Bz112c-LgbsSe-OWXEXe-SfQLQb-suEOdc hk9qKe  S5GDme gVYcob JsuyRc boDUxc")[1].click();
            googleMeetStart = true;
        }
    }else{
        googleMeetStart = true;
    }
    }

    function findSt(arr,st){
    for(let i=0; i<arr.length; i++){
        if(st==arr[i]){return true;}
    }
    return false;
    }

    allData = [];
    audioLooping = true;
	localStorage.setItem("audioLooping",JSON.stringify(audioLooping));
    audioChuckTime = 10000;

    async function storeData(){
    currentAudioChunk = null;
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    if (stream.getAudioTracks().length === 0) {
        throw new Error('No audio tracks available');
    }
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = event => {
        let reader = new FileReader();
        reader.onloadend = function(){
            if(reader.readyState === FileReader.DONE){
                currentAudioChunk = reader.result;
            }
        };
        reader.onerror = function(error) {
            console.error('Error reading the audio Blob :- ', error);
        };
        reader.readAsDataURL(event.data);
    };
    mediaRecorder.onstop = async () => {};
    mediaRecorder.start();
    time=[];
    now = new Date();
    time.push(now.getHours()+":"+now.getMinutes()+":"+now.getSeconds());
    time.push(now.getHours()+":"+now.getMinutes()+":"+(now.getSeconds()+10));
    allAttendees = [];
    attendence = true;
    activeMike = [];
    changeInVoice=[];

    intervalId = setInterval(()=>{
        data1 = document.getElementsByClassName("AE8xFb OrqRRb GvcuGe goTdfd");
        data1Ch = data1[0].children;
        data1Ch = Array.from(data1Ch);
        data1Ch.forEach((element,index) => {

            if(attendence){
                allAttendees.push(element.children[0].children[1].children[0].children[0].innerText);
            }

            if(index==0 ? element.children[1].children[0].children[0].children[0].className == 'JHK7jb Nep7Ue I118Fc ' : element.children[1].children[0].children[0].children[0].children[2].children[0].className == 'JHK7jb Nep7Ue '){
                
                if( activeMike.length===0 || !findSt(activeMike,element.children[0].children[1].children[0].children[0].innerText) ){
                    activeMike.push(element.children[0].children[1].children[0].children[0].innerText);
                }
                
                index==0 ? temp = element.children[1].children[0].children[0].children[0].children[0].children[1] : temp = element.children[1].children[0].children[0].children[0].children[2].children[0].children[0];

                if( index==0 ? temp.className != "IisKdb GF8M7d  gjg47c KUNJSe x9nQ6" : temp.className != "IisKdb GF8M7d  gjg47c MNVeFb kT2pkb" ){
                    if(!findSt(changeInVoice,element.children[0].children[1].children[0].children[0].innerText) || changeInVoice.length===0){
                        changeInVoice.push(element.children[0].children[1].children[0].children[0].innerText);
                    }
                }
            }
        });
        attendence = false;
    },1);

    setTimeout(async()=>{currentAudioChunk = null; mediaRecorder.stop(); clearInterval(intervalId);
        if(audioLooping){storeData();}
        await new Promise((resolve)=>{checkInt = setInterval(()=>{
                if(currentAudioChunk != null){clearInterval(checkInt); resolve();}},100);});
        allData.push([time,allAttendees,activeMike,changeInVoice,currentAudioChunk]);
        if(allData.length >12){allData = allData.slice(1,allData.length);}
        localStorage.setItem("audioData",JSON.stringify(allData));},audioChuckTime);
    }

    function clearDataInterval(){
    temp = document.getElementsByClassName("R5ccN")[0].children[7].children[0].children[0];
    temp.addEventListener("click",()=>{ 
        audioLooping = false; 
		localStorage.setItem("audioLooping",JSON.stringify(audioLooping));
    });
    }

    CheckMeetInt = setInterval(()=>{
    googleMeetCheck();
    if(googleMeetStart){
        clearInterval(CheckMeetInt);
        storeData();
        clearDataInterval();}},100);
    """
	





class JS_MicrosoftTeamsBot(object):
	js_code = """teamsMeetStart = false
function teamsMeetCheck(){
    iframeDom = document.querySelector("body").children[10].children[0].children[0].contentWindow.document
    if(iframeDom.getElementsByClassName("fui-Flex ___1x4ppn3 f22iagw f1vx9l62 fly5x3f f1l02sjl fqaeacu f1immsc2")[0] == undefined){
        iframeDom.getElementsByClassName("fui-Toolbar ___1g46m4l f22iagw f122n59 f1g0x7ka fhxju0i f1qch9an f1cnd47f")[1].children[3].click()
        teamsMeetStart = true                               
    }
    if(iframeDom.getElementsByClassName("fui-Flex ___1x4ppn3 f22iagw f1vx9l62 fly5x3f f1l02sjl fqaeacu f1immsc2")[0] != undefined){
        teamsMeetStart = true                               
    }
}

function findSt(arr,st){
    for(let i=0; i<arr.length; i++){
        if(st==arr[i]){return true}
    }
    return false
}

allData = []  // Store the last 2 minutes data
audioLooping = true
localStorage.setItem("audioLooping",JSON.stringify(audioLooping));
audioChuckTime = 10000 

async function storeData(){
    currentAudioChunk = null
    
    stream = await navigator.mediaDevices.getUserMedia({ audio : true });

    mediaRecorder = new MediaRecorder(stream); // new mediaRecoding component for every loop
    
    mediaRecorder.ondataavailable = event => { // the function will get the available data and send it to current Audio Chunk 
        let reader = new FileReader()
        reader.onloadend = function(){
            if(reader.readyState === FileReader.DONE){
                currentAudioChunk = reader.result;
            }
        }
        reader.onerror = function(error) {
            console.error('Error reading the audio Blob :- ', error);
        };
        reader.readAsDataURL(event.data)
        // console.log(event.data)
    };

    mediaRecorder.onstop = async () => {
        // audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        // console.log("on stop")
    };

    mediaRecorder.start() // on start of mediaRecorder
    
    time=[]                                                                             // time variable 
    now = new Date()                                                                    // update date 
    time.push(now.getHours()+":"+now.getMinutes()+":"+now.getSeconds())             
    time.push(now.getHours()+":"+now.getMinutes()+":"+(now.getSeconds()+10))
    allAttendees = []                                                                   // update all Attendees
    attendence = true                                                                   // once the attendees are stores it change to false
    activeMike = []                                                                     // update all active Mike in the session
    changeInVoice=[]         

    intervalId = setInterval( ()=>{
        try{
            iframeDom = document.querySelector("body").children[10].children[0].children[0].contentWindow.document
            data1 = iframeDom.getElementsByClassName("virtual-tree-list-scroll-container")[0].children[0].children
            data1Ch = Array.from(data1)
            data1Ch.forEach( (element,index)=>{
                if(index != 0 ){
    
                    if(attendence){
                        allAttendees.push(element.children[0].children[0].children[0].children[1].children[0].innerText)
                    }
    
                    if(element.children[0].children[0].children[0].children[2].children[0].children[0].children[0].getAttribute('aria-label')=='Unmuted'){
                        if(activeMike.length===0 || !findSt(activeMike,element.children[0].children[0].children[0].children[1].children[0].innerText)){
                            activeMike.push(element.children[0].children[0].children[0].children[1].children[0].innerText)
                        }
                        
                        if(element.children[0].children[0].children[0].children[0].children[0].className != 'ui-avatar e jw fo by jx qn qo qp qq qr qs qt qu qv qw qx qy gx gy gz ha qz ra rb rc gp rd go undefined lpcCommonWeb-hoverTarget container-161'){
                            if(changeInVoice===0 || !findSt(changeInVoice,element.children[0].children[0].children[0].children[1].children[0].innerText)){
                                changeInVoice.push(element.children[0].children[0].children[0].children[1].children[0].innerText)
                            }
                        }
                    }
                    
                }
            })
        }catch(err){
            console.log("in people iteration")
        }
        attendence = false
    },1)

    setTimeout(async()=>{
        currentAudioChunk = null 
        
        mediaRecorder.stop()

        clearInterval(intervalId)

        if(audioLooping){storeData()}

        await new Promise( (resolve)=>{
            checkInd = setInterval(()=>{
                if(currentAudioChunk != null){
                    clearInterval(checkInd)
                    resolve()
                }
            },100)
        })

        allData.push([time,allAttendees,activeMike,changeInVoice,currentAudioChunk])

        if(allData.length > 9){
            allData = allData.slice(1,allData.length)
        }

        localStorage.setItem("audioData",JSON.stringify(allData))
        // console.log(allData)

    },audioChuckTime)
}

function clearDataInterval(){
    iframeDom = document.querySelector("body").children[10].children[0].children[0].contentWindow.document
    temp = iframeDom.getElementById("hangup-button")
    temp.addEventListener("click",()=>{ 
        audioLooping = false 
		localStorage.setItem("audioLooping",JSON.stringify(audioLooping));
    })
}

CheckMeetInd = setInterval( ()=>{
    teamsMeetCheck()
    if(teamsMeetStart){
        clearInterval(CheckMeetInd)
        storeData()
        clearDataInterval()
    }
},100 )
    """
	


class JS_ZoomBot(object):
	js_code = """iframeDom = null
function updateIframe(){
    try{

        if(document.body.className != 'ReactModal__Body--open _ColorsLight_pc0r7_3 _root_1uvq9_1'){
            iframeDom = document.children[0].children[1].children[1].children[2].children[0].children[0].contentWindow.document.body
        }else{
            iframeDom = document.body
        }
    }catch(err){
        console.log("error in update Iframe")
    }
}

zoomMeetStart = false
async function zoomMeetCheck(){
    updateIframe()
    try{
        if(iframeDom.getElementsByClassName("footer-button-base__button ax-outline join-audio-container__btn")[0].innerText == "Join Audio" ){
            iframeDom.getElementsByClassName("zm-btn join-audio-by-voip__join-btn zm-btn--primary zm-btn__outline--white zm-btn--lg")[0].click()
        }
        else if(iframeDom.getElementsByClassName("footer-button-base__button ax-outline join-audio-container__btn")[0].innerText == "Mute"){
            iframeDom.getElementsByClassName("footer-button-base__button ax-outline join-audio-container__btn")[0].click()
        }
        else if(iframeDom.getElementsByClassName("meeting-client-inner")[0].children[0].children[1].style.visibility != 'visible'){
            iframeDom.getElementsByClassName("footer-button-base__button ax-outline footer-button__button")[0].click()
        }
        else{
            zoomMeetStart = true
        }
    }catch(err){
        throw err
    }   
}
// zoomMeetCheck()

function findSt(arr,st){
    for(let i=0; i<arr.length; i++){
        if(st==arr[i]){return true}
    }
    return false
}

allData = []
audioLooping = true
localStorage.setItem("audioLooping",JSON.stringify(audioLooping));
audioChuckTime = 10000

async function storeData(){
    currentAudioChunk = null

    stream = await navigator.mediaDevices.getUserMedia({audio : true});

    if(stream.getAudioTracks().length==0){
        throw new Error('No audio tracks available')
    }

    mediaRecorder = new MediaRecorder(stream)

    mediaRecorder.ondataavailable = event => { // the function will get the available data and send it to current Audio Chunk 
        let reader = new FileReader()
        reader.onloadend = function(){
            if(reader.readyState === FileReader.DONE){
                currentAudioChunk = reader.result;
            }
        }
        reader.onerror = function(error) {
            console.error('Error reading the audio Blob :- ', error);
        };
        reader.readAsDataURL(event.data)
    };
    mediaRecorder.onstop = async () => {
        // audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        // console.log("on stop")
    };
    mediaRecorder.start()

    time=[]                                                                             // time variable 
    now = new Date()                                                                    // update date 
    time.push(now.getHours()+":"+now.getMinutes()+":"+now.getSeconds())             
    time.push(now.getHours()+":"+now.getMinutes()+":"+(now.getSeconds()+10))
    allAttendees = []                                                                   // update all Attendees
    attendence = true                                                                   // once the attendees are stores it change to false
    activeMike = []                                                                     // update all active Mike in the session
    changeInVoice=[]

    intervalId = setInterval( ()=>{
        updateIframe()
        data1 = iframeDom.getElementsByClassName("participants-wrapper__inner")[0].children[0].children[0].children[0].children
        data1Ch = Array.from(data1)
        data1Ch.forEach(element => {
            try{
                if(attendence){
                    allAttendees.push(element.children[0].children[0].children[0].children[0].children[1].children[0].innerText)
                }
                
                if(element.children[0].children[0].children[0].children[1].children[0].children[0].children[0].className['baseVal'] == "lazy-svg-icon__icon lazy-icon-icons/participants-list/audio-unmuted-1" ){
                    if(activeMike.length===0 || !findSt(activeMike,element.children[0].children[0].children[0].children[0].children[1].children[0].innerText) ){
                        activeMike.push(element.children[0].children[0].children[0].children[0].children[1].children[0].innerText)
                    }
                } 
    
                if(element.children[0].children[0].children[0].children[1].children[0].children[0].children[0].className['baseVal']==undefined){
                    if(changeInVoice===0 || !findSt(changeInVoice,element.children[0].children[0].children[0].children[0].children[1].children[0].innerText) ){
                        changeInVoice.push( element.children[0].children[0].children[0].children[0].children[1].children[0].innerText )
                    }
                }
            }catch(err){
                console.log("undefine in participation column")
            }
            
        });
        attendence = false
    }, 1 )

    setTimeout( async()=>{
        currentAudioChunk = null
        mediaRecorder.stop()
        clearInterval(intervalId)
        if(audioLooping){storeData()}

        // console.log(currentAudioChunk)
        await new Promise( (resolve)=>{
            checkInd = setInterval( ()=>{
                if(currentAudioChunk != null){
                    clearInterval(checkInd)
                    resolve()
                }
            },100 )
        })
        // console.log(currentAudioChunk)
        allData.push([time,allAttendees,activeMike,changeInVoice,currentAudioChunk])
        if(allData.length > 12){
            allData = allData.slice(1,allData.length)
        }
        localStorage.setItem("audioData",JSON.stringify(allData))
        // console.log(allData)
    }, audioChuckTime )
}
 
function clearDataInterval(){
    updateIframe()
    temp = iframeDom.getElementsByClassName("footer-button-base__button ax-outline footer-button__button")[3]
    temp.addEventListener("click",()=>{
        console.log("audio looping is false")
        audioLooping = false
		localStorage.setItem("audioLooping",JSON.stringify(audioLooping));
    })
}

updateIframe()
checkMeetInd = setInterval( ()=>{
    zoomMeetCheck()
    if(zoomMeetStart){
        clearInterval(checkMeetInd)
        storeData()
        clearDataInterval()
    }
} )"""