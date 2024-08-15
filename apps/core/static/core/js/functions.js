export function validate(evt) {
  let theEvent = evt || window.event;

  let key = theEvent.keyCode || theEvent.which;

  key = String.fromCharCode(key);

  const regex = /[0-9]|\./;

  if (!regex.test(key)) {
    theEvent.returnValue = false;
    if (theEvent.preventDefault) theEvent.preventDefault();
  }
}

//функция получения куки
export function getCookie(name) {
  let matches = document.cookie.match(
    new RegExp(
      "(?:^|; )" +
      name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") +
      "=([^;]*)"
    )
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

//функция создания куки
export function setCookie(name, value, options = {}) {
  options = {
    ...options,
  };

  if (options.expires instanceof Date) {
    options.expires = options.expires.toUTCString();
  }

  let updatedCookie = name + "=" + value;

  for (let optionKey in options) {
    updatedCookie += "; " + optionKey;
    let optionValue = options[optionKey];
    if (optionValue !== true) {
      updatedCookie += "=" + optionValue;
    }
  }
  document.cookie = updatedCookie;
}

// функция удаления куки
export function deleteCookie(name, path, domain) {
  if (getCookie(name)) {
    document.cookie = `${name}=; Path=${path}; Max-Age=-1;`
    // document.cookie =
    // name + "=; Path=" + path + "; Domain=" + domain + "; Max-Age=-1;";
  }

}