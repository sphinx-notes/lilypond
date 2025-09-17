document.addEventListener('DOMContentLoaded', function() {
    const players = document.querySelectorAll('div.sphinxnotes-lilypond');
    
    players.forEach(player => {
        const select = player.querySelector('select');
        const audio = player.querySelector('audio');
        if (!select || !audio) {
            return
        }
        
        select.addEventListener('change', function() {
            if (this.value) {
                audio.src = this.value;
            } else {
                audio.src = this.options[0];
            }
        });
    });
});
