function Company(nameCompany) {
  this.name = nameCompany;
  this.returnName = returnName;
}
function returnName() {
  return this.name;
}

const obj = new Company("Google");
console.log(obj.returnName();
