const loadCountries = (countries, lang) => {
    countries.forEach((country) => {
        let countryName;
        if (lang == "en") {
            countryName = country.nameEN;
        } else {
            countryName = country.nameAR;
        }
        $("#Country").append(
            "<option" +
                ' value="' +
                `${country.nameEN}-${country.nameAR}` +
                '">' +
                countryName +
                "</option>"
        );
    });
    $("#Country").selectpicker("refresh");
};
$(document).ready(() => {
    $("#preloader").remove();
    $("#id_message").on("input", function () {
        autoExpand($(this));
    });
    if (
        window.location.href.indexOf("update") > -1 ||
        window.location.href.indexOf("register") > -1
    ) {
        let jsonPath =
            window.location.origin + "/staticfiles/json/countries.json";
        const lang = JSON.parse(document.getElementById("lang").textContent);
        fetch(jsonPath)
            .then((response) => response.json())
            .then((data) => loadCountries(data, lang))
            .then(() => {
                if (window.location.href.indexOf("update") > -1) {
                    let country = $("#Country").find("option:selected");
                    $("#Country option").map(function () {
                        if (this.value == country.val() && !this.selected) {
                            this.remove();
                        }
                    });
                }
            });
    }
});
function autoExpand(field) {
    field.height("36px");
    const computed = window.getComputedStyle(field[0]);
    const height =
        parseInt(computed.getPropertyValue("border-top-width"), 10) +
        parseInt(computed.getPropertyValue("padding-top"), 10) +
        field[0].scrollHeight +
        parseInt(computed.getPropertyValue("padding-bottom"), 10) +
        parseInt(computed.getPropertyValue("border-bottom-width"), 10);
    field.height(height + "px");
}
