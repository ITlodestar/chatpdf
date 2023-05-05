let Allfiles = [];

$(document).ready(function () {
  $('#spinner').hide();
  $("#question").on('keyup', function (e) {
    if (e.key === 'Enter' || e.keyCode === 13) {
      upload()
    }
  });
  $('#run').click(function (event) {
    event.preventDefault();  // Prevent form from submitting normally
    upload()
  });
});

function upload() {
  const answer_panel = document.getElementById("answers");
  let myquestion = document.getElementById("question");
  answer_panel.innerHTML += "<div class='d-flex justify-content-end m-2'><div class='chat-message'>" + myquestion.value + "</div></div>"
  console.log(answer_panel.scrollHeight);
  answer_panel.scrollTop = answer_panel.scrollHeight + 30;

  const formData = new FormData();
  for (var i = 0; i < Allfiles.length; i++) {
    formData.append("files[]", Allfiles[i]);
  }
  formData.append('myquestion', myquestion.value);
  console.log(Allfiles);
  myquestion.value = "";
  // Button stlye - hide or show
  Running();

  $.ajax({
    url: '/upload',
    method: 'POST',
    data: formData,
    processData: false,
    contentType: false,
    success: function (response) {
      EndRunning()
      answer_panel.innerHTML += "<div class=' justify-content-start d-flex  m-2'><div  class='chat-message'>" + response + "</div></div>";
    },
    error: function (error) {
      EndRunning()
      answer_panel.innerHTML += "<h3 class='d-flex justify-content-start   m-2'><div class='chat-message text-danger'>" + error.statusText + "</div></h3>";
    }
  });
}

function Running() {
  $('#spinner').show();
  $('#buttonRun').hide();
  $('#question').prop('disabled', true);
  $('#run').prop('disabled', true);
}

function EndRunning() {
  $('#spinner').hide();
  $('#buttonRun').show();
  $('#question').prop('disabled', false);
  $('#run').prop('disabled', false);
}
document.addEventListener('DOMContentLoaded', () => {
  // ************************ Drag and drop ***************** //
  let dropArea = document.getElementById("drop-area")

    // Prevent default drag behaviors
    ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, preventDefaults, false)
      document.body.addEventListener(eventName, preventDefaults, false)
    })

    // Highlight drop area when item is dragged over it
    ;['dragenter', 'dragover'].forEach(eventName => {
      dropArea.addEventListener(eventName, highlight, false)
    })

    ;['dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, unhighlight, false)
    })

  // Handle dropped files
  dropArea.addEventListener('drop', handleDrop, false)

})

function preventDefaults(e) {
  e.preventDefault()
  e.stopPropagation()
}

function highlight(e) {
  let dropArea = document.getElementById("drop-area")
  dropArea.classList.add('highlight')
}

function unhighlight(e) {
  let dropArea = document.getElementById("drop-area")
  dropArea.classList.remove('active')
}

function handleDrop(e) {
  var dt = e.dataTransfer
  var files = dt.files

  handleFiles(files)
}


function handleFiles(files) {

  Allfiles.push(...files);
  console.log(Allfiles);
  addFiles(Allfiles, files)
}

class CustomFileList {
  constructor(files) {
    this.length = files.length;
    this.files = files;
  }
}

function addFiles(files, addfiles) {
  const fileInputpreview = document.getElementById('gallery');
  let newFiles = new CustomFileList([]);
  for (let i = 0; i < addfiles.length; i++) {
    newFiles.files.push(addfiles[i]);

    let fileInputItem = document.createElement('div');
    fileInputItem.classList.add("file-input-item");
    fileInputItem.innerHTML = `
      <span>${addfiles[i].name}</span>
      <button type="button" data-index="${i}" class="btn-close btn-close-white remove-button" aria-label="Close"></button>
    `;

    fileInputItem.querySelector(".remove-button").addEventListener("click", (event) => {
      let index = event.target.dataset.index;
      let newFiles = new CustomFileList([]);
      for (let j = 0; j < fileInputpreview.files.length; j++) {
        if (j != index) {
          newFiles.files.push(fileInputpreview.files[j])
        }
      }


      Allfiles = Allfiles.filter(function (item) {
        return item.name != files[index].name;
      });

      fileInputpreview.files = new CustomFileList(newFiles.files);
      fileInputItem.remove();
    });
    fileInputItem.dataset.index = i;
    fileInputpreview.parentElement.insertBefore(fileInputItem, fileInputpreview.nextSibling);
  }
  fileInputpreview.files = new CustomFileList(newFiles.files);
}
