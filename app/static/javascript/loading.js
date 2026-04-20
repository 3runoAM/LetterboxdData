fetch('/api/process-data', {method: 'POST'})
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = "/perfil";
        } else {
            window.location.href = "/";
        }
    })
    .catch(err => {
        console.error(err);
        window.location.href = "/";
    });