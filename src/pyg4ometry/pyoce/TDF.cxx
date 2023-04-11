#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <TDF.hxx>
#include <TDF_Attribute.hxx>
#include <TDF_AttributeIterator.hxx>
#include <TDF_Data.hxx>
#include <TDF_Label.hxx>
#include <TDF_LabelSequence.hxx>
#include <TDF_TagSource.hxx>
#include <TDF_Tool.hxx>
#include <TDF_IDFilter.hxx>
#include <TCollection_ExtendedString.hxx>
#include <Standard_GUID.hxx>
#include <Standard_Transient.hxx>
#include <TDataStd_Name.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true);

PYBIND11_MODULE(TDF, m) {
  py::class_<TDF>(m,"TDFClass")
    .def_static("LowestID",&TDF::LowestID)
    .def_static("UppestID",&TDF::UppestID)
    .def_static("AddLinkGUIDToProgID",&TDF::AddLinkGUIDToProgID)
    .def_static("GUIDFromProgID",&TDF::GUIDFromProgID)
    .def_static("ProgIDFromGUID",&TDF::ProgIDFromGUID);

  py::class_<TDF_Attribute, opencascade::handle<TDF_Attribute>, Standard_Transient> (m,"TDF_Attribute")
    .def("Label",&TDF_Attribute::Label);

  py::class_<TDF_AttributeIterator>(m, "TDF_AttributeIterator")
    .def(py::init<>())
    .def(py::init<const TDF_Label &, const Standard_Boolean>())
    .def(py::init<const TDF_LabelNodePtr , const Standard_Boolean>())
    .def("Initialize",&TDF_AttributeIterator::Initialize)
    .def("More",&TDF_AttributeIterator::More)
    .def("Next",&TDF_AttributeIterator::Next)
    .def("Value",&TDF_AttributeIterator::Value)
    .def("PtrValue",&TDF_AttributeIterator::PtrValue);

  py::class_<TDF_Data, opencascade::handle<TDF_Data>, Standard_Transient>(m,"TDF_Data");

  py::class_<TDF_Label> (m,"TDF_Label")
    .def(py::init<>())
    .def("Data", &TDF_Label::Data)
    .def("Depth", &TDF_Label::Depth)
    .def("Father", &TDF_Label::Father)
    .def("FindAttribute", [](TDF_Label &label, const Standard_GUID & guid, opencascade::handle<TDF_Attribute> &attribute) { auto ret = label.FindAttribute(guid,attribute); return py::make_tuple(ret, attribute);})
    .def("FindAttribute", [](TDF_Label &label, const Standard_GUID & guid, const Standard_Integer aTransaction, opencascade::handle<TDataStd_Name> &attribute) { auto ret =  label.FindAttribute(guid,aTransaction,attribute); return py::make_tuple(ret,attribute);})
    .def("FindChild", [](TDF_Label &label, const Standard_Integer tag, const Standard_Boolean create) {auto retLabel = label.FindChild(tag,create); return py::make_tuple(!retLabel.IsNull(), retLabel);})
    .def("HasAttribute", &TDF_Label::HasAttribute)
    .def("HasChild", &TDF_Label::HasChild)
    .def("IsDifferent", &TDF_Label::IsDifferent)
    .def("IsAttribute",&TDF_Label::IsAttribute)
    .def("IsEqual", &TDF_Label::IsEqual)
    .def("IsNull", &TDF_Label::IsNull)
    .def("IsRoot",&TDF_Label::IsRoot)
    .def("NewChild", &TDF_Label::NewChild)
    .def("NbAttributes", &TDF_Label::NbAttributes)
    .def("NbChildren", &TDF_Label::NbChildren)
    .def("Nullify", &TDF_Label::Nullify)
    .def("Root", &TDF_Label::Root)
    .def("Tag", &TDF_Label::Tag)
    .def("Transaction", &TDF_Label::Transaction)
    .def("Dump",[](TDF_Label &label) { py::scoped_ostream_redirect output; label.Dump(std::cout);})
    .def("EntryDump",[](TDF_Label &label) { py::scoped_ostream_redirect output; label.EntryDump(std::cout);});

  py::class_<TDF_LabelSequence>(m,"TDF_LabelSequence")
    .def(py::init<>())
    .def("Size",&TDF_LabelSequence::Size)
    .def("begin",&TDF_LabelSequence::begin)
    .def("end",&TDF_LabelSequence::end)
    .def("Dump",[](TDF_LabelSequence &ls) { return;})
    .def("Value",&TDF_LabelSequence::Value)
    .def("__iter__",[](const TDF_LabelSequence &s) { return py::make_iterator(s.begin(), s.end()); }, py::keep_alive<0, 1>())
    .def("__call__",[](TDF_LabelSequence &ls, Standard_Integer i) { return ls(i);});

  py::class_<TDF_TagSource, opencascade::handle<TDF_TagSource>, TDF_Attribute>(m,"TDF_TagSource")
    .def(py::init<>())
    .def("Get",&TDF_TagSource::Get)
    .def_static("GetID",&TDF_TagSource::GetID);

  py::class_<TDF_Tool>(m,"TDF_Tool")
    .def_static("Entry",&TDF_Tool::Entry)
    .def_static("Label",[](const opencascade::handle<TDF_Data> &aDF,
                           const TCollection_AsciiString &anEntry,
                           TDF_Label &aLabel,
                           const Standard_Boolean create) {
                           TDF_Tool::Label(aDF, anEntry, aLabel, create);
                           return aLabel;
                           })
    .def_static("NbAttributes",[](TDF_Tool &tool,
                                  const TDF_Label& label) {
                                  return TDF_Tool::NbAttributes(label);
                                  })
    .def_static("NbAttributes",[](TDF_Tool &tool,
                                  const TDF_Label& label,
                                  const TDF_IDFilter &filter) {
                                  return TDF_Tool::NbAttributes(label,filter);
                                  })
    .def_static("NbLabels",&TDF_Tool::NbLabels);
}