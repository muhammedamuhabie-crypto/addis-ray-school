document.addEventListener('DOMContentLoaded',()=>{

    document.querySelectorAll('form').forEach(f=>{
        f.addEventListener('submit',()=>{
            const b=f.querySelector('button[type="submit"],button:not([type])');
            if(b&&f.checkValidity())
                setTimeout(()=>{
                    b.disabled=true;
                    b.dataset.original=b.textContent;
                    b.textContent='Saving...';
                },0)
        })
    });


    const grade=document.getElementById('id_grade');
    const section=document.getElementById('id_section');
    const stream=document.getElementById('id_stream');
    const student=document.getElementById('id_student');

    if(!grade || !section || !stream || !student){
        return;
    }


    function loadStudents(){

        const selectedGrade=grade.value;
        const selectedSection=section.value;
        const selectedStream=stream.value;

        student.innerHTML='<option value="">Loading students...</option>';


        if(!selectedGrade || !selectedSection){

            student.innerHTML='<option value="">Select grade and section first</option>';
            return;
        }


        if(
            (selectedGrade === '11' || selectedGrade === '12')
            && !selectedStream
        ){

            student.innerHTML='<option value="">Select stream first</option>';
            return;
        }


        let url='/students/filter/?grade='
            + encodeURIComponent(selectedGrade)
            + '&section='
            + encodeURIComponent(selectedSection);


        if(selectedStream){

            url += '&stream='
                + encodeURIComponent(selectedStream);

        }


        fetch(url)
            .then(response=>response.json())
            .then(data=>{

                student.innerHTML='';


                if(data.students.length===0){

                    student.innerHTML=
                        '<option value="">No students found</option>';

                    return;
                }


                const firstOption=document.createElement('option');

                firstOption.value='';
                firstOption.textContent='Select student';

                student.appendChild(firstOption);


                data.students.forEach(s=>{

                    const option=document.createElement('option');

                    option.value=s.id;

                    option.textContent=
                        s.student_id
                        + ' - '
                        + s.name;

                    student.appendChild(option);

                });

            })
            .catch(error=>{

                console.error('Student loading error:',error);

                student.innerHTML=
                    '<option value="">Unable to load students</option>';

            });

    }


    grade.addEventListener('change',loadStudents);
    section.addEventListener('change',loadStudents);
    stream.addEventListener('change',loadStudents);

});


/* =========================================
   DARK MODE
   ========================================= */

(function () {
    const root = document.documentElement;
    const toggle = document.getElementById("theme-toggle");
    const icon = document.getElementById("theme-icon");

    if (!toggle) {
        return;
    }

    function applyTheme(theme) {
        if (theme === "dark") {
            root.classList.add("dark-mode");
            icon.textContent = "Light";
            toggle.setAttribute("aria-label", "Switch to light mode");
            toggle.setAttribute("title", "Switch to light mode");
        } else {
            root.classList.remove("dark-mode");
            icon.textContent = "Dark";
            toggle.setAttribute("aria-label", "Switch to dark mode");
            toggle.setAttribute("title", "Switch to dark mode");
        }
    }

    const savedTheme = localStorage.getItem("addisRayTheme") || "light";

    applyTheme(savedTheme);

    toggle.addEventListener("click", function () {
        const newTheme = root.classList.contains("dark-mode")
            ? "light"
            : "dark";

        localStorage.setItem("addisRayTheme", newTheme);

        applyTheme(newTheme);
    });
})();
