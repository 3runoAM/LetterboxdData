const botoes = document.querySelectorAll(".view-button");
const paineis = document.querySelectorAll(".panel");

console.log(botoes)
console.log(paineis)

botoes.forEach(botao => {
    botao.addEventListener("click", function() {

        botoes.forEach(b => b.classList.remove("active"));
        this.classList.add("active");

        const alvo = this.dataset.target;
        paineis.forEach(p => p.classList.remove("active"));
        document.getElementById(alvo).classList.add("active");
    });
});