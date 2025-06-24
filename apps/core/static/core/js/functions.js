//Класс для разделения чила на разряды
export class NumberParser {
  constructor(locale) {
    const parts = new Intl.NumberFormat(locale).formatToParts(12345.6);
    const numerals = [
      ...new Intl.NumberFormat(locale, { useGrouping: false }).format(
        9876543210
      ),
    ].reverse();
    const index = new Map(numerals.map((d, i) => [d, i]));
    this._group = new RegExp(
      `[${parts.find((d) => d.type === "group").value}]`,
      "g"
    );
    this._decimal = new RegExp(
      `[${parts.find((d) => d.type === "decimal").value}]`
    );
    this._numeral = new RegExp(`[${numerals.join("")}]`, "g");
    this._index = (d) => index.get(d);
  }
  parse(string) {
    return (string = string
      .trim()
      .replace(this._group, "")
      .replace(this._decimal, ".")
      .replace(this._numeral, this._index))
      ? +string
      : NaN;
  }
}

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
    document.cookie = `${name}=; Path=${path}; Max-Age=-1;`;
  }
}

// функция отображения ошибки при валидации формы
export function showErrorValidation(description, error) {
  error.textContent = description;
  error.classList.add("show");
  setTimeout(() => {
    error.classList.remove("show");
  }, 2000);
}

// валидация Email
export function isEmailValid(value) {
  const emailValidate =
    /^(([^<>()[\].,;:\s@"]+(\.[^<>()[\].,;:\s@"]+)*)|(".+"))@(([^<>()[\].,;:\s@"]+\.)+[^<>()[\].,;:\s@"]{2,})$/iu;
  return emailValidate.test(value);
}

//Функция для orderMultiplicity
export let getClosestInteger = (a, b, x = Math.trunc(a / b)) => {
  //х - сколько раз b содержится в а
  if (a > b) {
    //защита от дурака
    if (!(a % b))
      //если а делится на b без остатка
      return a; //значит а это и есть ответ
    return b * x == 1000 ? b * x - b : b * x; //иначе выбираем между b * x
  }
  return "Некорректный ввод данных";
};

export function getCurrentPrice(p) {
  const price = p.replace(",", ".");
  return price;
}
// Отследить кол-во знаков после запятой
const numQuantity = (value) =>
  value.toString().includes("," || ".")
    ? value
        .toString()
        .split("," || ".")
        .pop().length
    : 0;

// Форматирования числового значения с разрядом, для отображения
export const getDigitsNumber = (container, value) => {
  let currentValue = new Intl.NumberFormat("ru")
    .format(+value)
    .replace(/(\d+)(\.|,)(\d+)/g, function (o, a, b, c) {
      return a + b + c.slice(0, 2);
    });
  if (numQuantity(currentValue) == 1) {
    currentValue += "0";
  } else if (numQuantity(currentValue) == 0) {
    currentValue += ",00";
  } else {
    currentValue;
  }
  container.textContent = currentValue;
};

//Валидатор даты(возвращает даду спецификации по самой поздней дате поставки конкретного товара)
export function getDeliveryDate(dates) {
  const arrayDateValues = [];
  dates.forEach((el) => {
    const elValue = Date.parse(el.value);
    arrayDateValues.push(elValue);
  });
  const sortingArr = arrayDateValues.sort((a, b) => a - b);
  const maxDateValue = sortingArr.at(-1);
  const now = Date.now();
  const resultSecs = maxDateValue - now;
  const resultDays = Math.floor(resultSecs / 86400000);
  let result;
  if (resultDays <= 7) {
    result = "1 неделя";
  } else if (resultDays > 7 && resultDays <= 14) {
    result = "2 недели";
  } else if (resultDays > 14 && resultDays <= 21) {
    result = "3 недели";
  } else {
    const mounthQuantity = Math.ceil(resultDays / 30);

    function setMounth(value, words) {
      value = Math.abs(value) % 100;
      var num = value % 10;
      if (value > 10 && value < 20) return words[2];
      if (num > 1 && num < 5) return words[1];
      if (num == 1) return words[0];
      return words[2];
    }
    result = isNaN(mounthQuantity)
      ? "1 месяц"
      : `${mounthQuantity} ${setMounth(mounthQuantity, [
          "месяц",
          "месяца",
          "месяцев",
        ])}`;
  }
  return result;
}

//маска для телефона, с первой заменой цифры на 8
export const maskOptions = {
  mask: "+{7} (000) 000-00-00",
  prepare: function (appended, masked) {
    if (appended === "8" && masked.value === "") {
      return "7";
    }
    return appended;
  },
};

// прелодер на кнопку
export function setPreloaderInButton(button) {
  button.disabled = true;
  button.setAttribute("button-text", button.textContent);
  button.textContent = "";
  button.innerHTML = "<div class='small_loader'></div>";
}

// возвращение кнопки в активное состояние
export function hidePreloaderAndEnabledButton(button) {
  button.innerHTML = "";
  button.textContent = button.getAttribute("button-text");
  button.disabled = false;
}
