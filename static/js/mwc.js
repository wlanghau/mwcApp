function autocalculate(comp){
     var prep = document.getElementById("prepared-"+comp).value;
     if (prep == '0'){
        document.getElementById("served-"+comp).value = 0;
        document.getElementById("leftover-"+comp).value = 0;
     }
     var served = document.getElementById("served-"+comp).value;
     var leftover = document.getElementById("leftover-"+comp).value;
     document.getElementById("wastedNum-"+comp).innerHTML = prep - served - leftover;
     document.getElementById("wasted-"+comp).value = prep - served - leftover;
  }

$(document).ready(function(){
    // $('[data-toggle="tooltip"]').tooltip();

    $('#btn_comp_add').click(function(){
        var comp_to_add = $( "#add_component_list option:selected" ).text();
        var school = $("#school").attr('placeholder');
        var meal = $("#meal").attr('placeholder');

        var comp_planned = null;
        $.get('/get_comp/'+school+'/'+meal+'/'+comp_to_add+'/', function(data){
            comp_planned=data;

            const markup = `
              <tr>
                 <th scope="row"> ${comp_to_add} </th>
                 <td>${comp_planned}</td>
                 <input type="hidden" name="planned-${comp_to_add}" value="${comp_planned}">
                 <td><input style="width:75px" type="number" id="prepared-${comp_to_add}" name="prepared-${comp_to_add}"
                    onchange="autocalculate('${comp_to_add}')" required></td>
                 <td><input style="width:75px" type="number" id="served-${comp_to_add}" name="served-${comp_to_add}"
                    onchange="autocalculate('${comp_to_add}')" required></td>
                 <td><input style="width:75px" type="number" id="leftover-${comp_to_add}" name="leftover-${comp_to_add}"
                    onchange="autocalculate('${comp_to_add}')" required></td>
                 <td id="wastedNum-${comp_to_add}" ></td>
                 <input type="hidden" id="wasted-${comp_to_add}" name="wasted-${comp_to_add}">
                 <td><input style="width:75px" type="number" id="extra-${comp_to_add}" name="extra-${comp_to_add}"></td>
                 <td><input type="text" id="notes-${comp_to_add}" name="notes-${comp_to_add}" placeholder="Any notes?"></td>
              </tr>
            `;

            $('#comp_table tr:last').after(markup);
            });
    });
});