export function showProfile() {
  const name = new URLSearchParams(location.search).get("name");
  document.getElementById("greeting").innerHTML = "Hello, " + name;
}
