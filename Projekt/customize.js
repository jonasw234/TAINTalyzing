/* Customize vulnscan report with this script.
 * This example script will colorize the taints based on their severity.
 * Taints with a severity of 100% will get the normal background color that is also used for the
 * list itself.
 * Taints with a severity of 50% will get the background color of the sinks list.
 * Taints with a severity in between these two will get a background color between these two.
 *
 * Only works with the default rule names in the CSS file and background-colors set in rgb()-style.
 */
var taints = document.getElementsByClassName('taint');
var severe = document.styleSheets[0].cssRules[0].style['background-color'].match(/[.?\d]+/g);
var medium = document.styleSheets[0].cssRules[1].style['background-color'].match(/[.?\d]+/g);

Array.forEach(taints, function(taint) {
    var severity = taint.innerText.split('Severity level: ')[1].split('%')[0];
    var distance = (severity - 50) / 50;
    taint.style.backgroundColor = "rgb(" +
        Math.round(distance * severe[0] + (1 - distance) * medium[0]) + ", " +
        Math.round(distance * severe[1] + (1 - distance) * medium[1]) + ", " +
        Math.round(distance * severe[2] + (1 - distance) * medium[2]) + ")";
});
